"""
데이터소스(ex. notion)에서 문서를 가져오는 모듈
"""

from typing import List, Dict, Any, Literal, Union
from notion_client import AsyncClient
from notion_client.errors import APIResponseError
from langchain_text_splitters import RecursiveCharacterTextSplitter

from core.config import settings
from core.exception import CustomException, ExceptionCase
from schemas.schemas import Document, DocumentInput, DocumentMetadata
from services.qdrant_service import QdrantService
from services.gemini import GeminiService


class NotionDataLoader:
    DATASOURCE = "notion"

    def __init__(self):
        self.notion = AsyncClient(auth=settings.NOTION_API_KEY)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len,
        )
        self.gemini = GeminiService()
        self.qdrant = QdrantService()

    def _get_text_from_block(self, block: Dict[str, Any]) -> str:
        """단일 블록에서 텍스트를 추출."""
        block_type = block.get("type")
        if not block_type:
            return ""

        # 'rich_text' 필드를 가진 블록 타입 처리
        if block_type in [
            "paragraph",
            "heading_1",
            "heading_2",
            "heading_3",
            "bulleted_list_item",
            "numbered_list_item",
            "toggle",
            "quote",
            "callout",
        ]:
            rich_text = block.get(block_type, {}).get("rich_text", [])
            return "".join([text.get("plain_text", "") for text in rich_text])

        # 자식 페이지 블록의 경우 페이지 제목을 텍스트로 사용
        elif block_type == "child_page":
            return block.get("child_page", {}).get("title", "")

        # 기타 텍스트가 없는 블록 타입(이미지, 파일 등)은 빈 문자열 반환
        return ""

    async def _recursively_fetch_blocks(
        self,
        block_id: str,
        page_id: str,
        updated_at: str,
        cache_page_updated_at: dict = {},
        recursive_page: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        주어진 블록 ID 하위의 모든 블록을 재귀적으로 탐색하고
        메타데이터와 함께 텍스트 데이터를 추출.
        """
        results = []

        try:
            # 페이지네이션을 처리하며 모든 자식 블록 가져오기
            paginated_blocks = await self.notion.blocks.children.list(block_id=block_id)
            children_blocks = paginated_blocks.get("results", [])

            next_cursor = paginated_blocks.get("next_cursor")
            while next_cursor:
                paginated_blocks = await self.notion.blocks.children.list(
                    block_id=block_id, start_cursor=next_cursor
                )
                children_blocks.extend(paginated_blocks.get("results", []))
                next_cursor = paginated_blocks.get("next_cursor")

            for block in children_blocks:
                # 현재 블록에서 텍스트 추출
                text_content = self._get_text_from_block(block)
                parent_type = block.get("parent", {})
                parent_page_id = parent_type.get("page_id")
                # 현재 블록의 pag_id 추출
                parent_type = block.get("parent", {})
                parent_page_id = parent_type.get("page_id")
                if parent_page_id:
                    page_id = parent_page_id
                    if page_id in cache_page_updated_at:
                        updated_at = cache_page_updated_at[page_id]
                    else:
                        page_info = await self.notion.pages.retrieve(page_id=page_id)
                        updated_at = page_info["last_edited_time"]
                        cache_page_updated_at[page_id] = updated_at

                if text_content:  # 텍스트가 있는 경우에만 추가
                    results.append(
                        {
                            "content": text_content,
                            "updated_at": updated_at,
                            "page_id": page_id,
                            "block_id": block_id,
                            "block_type": block.get("type"),
                        }
                    )

                # `recursive_page = False`일 경우 현재 페이지의 내용만 추출.
                if block.get("type") == "child_page":
                    if not recursive_page:
                        continue

                # 현재 블록이 자식을 가지고 있다면 재귀적으로 탐색
                if block.get("has_children"):
                    child_results = await self._recursively_fetch_blocks(
                        block_id=block["id"],
                        page_id=page_id,  # 부모 페이지의 ID와 시간을 그대로 전달
                        updated_at=updated_at,
                        cache_page_updated_at=cache_page_updated_at,
                        recursive_page=recursive_page,
                    )
                    results.extend(child_results)

        except APIResponseError as e:
            raise CustomException(
                exception_case=ExceptionCase.DATALOAD_ERROR,
                detail=f"Error fetching blocks for {block_id}: {e}",
            )

        return results

    async def _extract_text_from_notion(
        self, start_page_id: str, recursive_page: bool = False
    ) -> List[Dict[str, Any]]:
        """
        시작 페이지 ID를 받아 해당 페이지와 모든 하위 블록의 텍스트를 추출.
        RAG에 사용될 메타데이터를 포함한 리스트를 반환.

        Args:
            start_page_id (str): 텍스트 추출을 시작할 Notion 페이지의 ID

        Returns:
            List[Dict[str, Any]]: 벡터 DB에 저장될 데이터 딕셔너리 리스트
                                (예: [{'content': '...', 'updated_at': '...', 'page_id': '...', 'block_id': '...'}])
        """

        try:
            # 시작 페이지의 메타데이터(업데이트 시간)를 가져옵니다.
            page_info = await self.notion.pages.retrieve(page_id=start_page_id)
            updated_at = page_info.get("last_edited_time")

            # 페이지 자체의 제목도 content에 포함시킵니다.
            title_property = page_info.get("properties", {}).get("title", {})
            if title_property.get("type") == "title":
                page_title = "".join(
                    [t.get("plain_text", "") for t in title_property.get("title", [])]
                )
            else:
                page_title = "제목 없음"

            initial_data = [
                {
                    "content": page_title,
                    "updated_at": updated_at,
                    "page_id": start_page_id,
                }
            ]

            cache_page_updated_at = {start_page_id: updated_at}

            # 페이지 하위의 블록들을 재귀적으로 탐색하여 텍스트를 추출합니다.
            block_data = await self._recursively_fetch_blocks(
                block_id=start_page_id,
                page_id=start_page_id,
                updated_at=updated_at,
                cache_page_updated_at=cache_page_updated_at,
                recursive_page=recursive_page,
            )

            return initial_data + block_data

        except APIResponseError as e:
            raise CustomException(
                exception_case=ExceptionCase.DATALOAD_ERROR,
                detail=f"페이지 정보를 가져오는 데 실패했습니다 (ID: {start_page_id}): {e}",
            )
        except Exception as e:
            raise CustomException(
                exception_case=ExceptionCase.DATALOAD_ERROR,
                detail=str(e),
            )

    def _chunk_context(self, extract_results: List[dict]) -> List[Document]:
        """
        추출한 block 리스트를 받아서 청킹 후 document 반환.

        Args:
            extract_results: 노션 페이지에서 추출한 블록 리스트.
        """
        try:
            extract_results_dict = {}
            for block in extract_results:
                page_id = block["page_id"]
                updated_at = block["updated_at"]
                content = block.get("content")

                if page_id not in extract_results_dict:
                    extract_results_dict.update(
                        {page_id: {"updated_at": updated_at, "content": []}}
                    )
                extract_results_dict[page_id]["content"].append(content)

            document_list = []
            for page_id, item in extract_results_dict.items():
                corpus = "\n".join(item["content"])
                chunks = self.text_splitter.split_text(corpus)
                for chunk in chunks:
                    document = Document(
                        content=chunk,
                        datasource=self.DATASOURCE,
                        updated_at=item["updated_at"],
                        page_id=page_id,
                    )
                    document_list.append(document)

            return document_list

        except Exception as e:
            raise CustomException(
                exception_case=ExceptionCase.DATALOAD_ERROR, detail=str(e)
            )

    async def get_documents(
        self, page_id: str, recursive_page: bool = False
    ) -> List[Document]:
        try:
            extract_results = await self._extract_text_from_notion(
                start_page_id=page_id, recursive_page=recursive_page
            )
            document_list = self._chunk_context(extract_results)

            return document_list

        except Exception as e:
            raise CustomException(
                exception_case=ExceptionCase.DATALOAD_ERROR, detail=str(e)
            )

    async def upload_documents(
        self,
        page_id: str,
        authority_group: List[str],
        recursive_page: bool = True,
    ) -> None:
        try:
            extract_results = await self._extract_text_from_notion(
                start_page_id=page_id, recursive_page=recursive_page
            )
            document_list = self._chunk_context(extract_results)
            document_input_list = [
                DocumentInput(
                    embedding=await self.gemini.generate_embedding(
                        contents=document.content, task="RETRIEVAL_DOCUMENT"
                    ),
                    metadata=DocumentMetadata(
                        authority_group=authority_group,
                        **document.model_dump(),
                    ),
                )
                for document in document_list
            ]
            await self.qdrant.upsert_document(document_input_list)

        except Exception as e:
            raise CustomException(
                exception_case=ExceptionCase.DATALOAD_ERROR, detail=str(e)
            )


def get_data_loader(datasource: Literal["notion"]) -> Union[NotionDataLoader, None]:
    if datasource == "notion":
        return NotionDataLoader()
    else:
        return None
