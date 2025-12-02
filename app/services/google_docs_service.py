"""
Google Docs 통합 서비스
LH 토지진단 보고서를 Google Docs로 변환하여 저장
"""

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import Dict, Any, List, Optional
from datetime import datetime
import os
import re
from bs4 import BeautifulSoup


class GoogleDocsService:
    """Google Docs 통합 관리"""
    
    def __init__(self):
        """초기화"""
        self.credentials_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH", "./google_credentials.json")
        self.drive_folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "")
        self.docs_service = None
        self.drive_service = None
        
        # Google Docs 사용 가능 여부
        self.enabled = False
        
        try:
            if os.path.exists(self.credentials_path):
                self._initialize_services()
                self.enabled = True
                print("✅ Google Docs 연동 활성화")
            else:
                print("⚠️ Google Docs 연동 미설정 (credentials 없음)")
        except Exception as e:
            print(f"⚠️ Google Docs 초기화 실패: {e}")
            self.enabled = False
    
    def _initialize_services(self):
        """Google Docs 및 Drive 서비스 초기화"""
        # OAuth2 인증 스코프 설정
        scopes = [
            'https://www.googleapis.com/auth/documents',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # 서비스 계정 인증
        creds = Credentials.from_service_account_file(
            self.credentials_path,
            scopes=scopes
        )
        
        # Google Docs API 서비스
        self.docs_service = build('docs', 'v1', credentials=creds)
        
        # Google Drive API 서비스
        self.drive_service = build('drive', 'v3', credentials=creds)
    
    def html_to_google_docs_requests(self, html_content: str) -> List[Dict]:
        """
        HTML 콘텐츠를 Google Docs API 요청으로 변환
        
        Args:
            html_content: HTML 형식의 보고서 내용
            
        Returns:
            Google Docs API 요청 배치 리스트
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        requests = []
        current_index = 1
        
        # HTML body 내용 추출
        body_content = soup.find('body')
        if not body_content:
            return requests
        
        # 텍스트 및 스타일 추출
        for element in body_content.descendants:
            if element.name == 'h1':
                text = element.get_text(strip=True)
                requests.append({
                    'insertText': {
                        'location': {'index': current_index},
                        'text': text + '\n'
                    }
                })
                requests.append({
                    'updateParagraphStyle': {
                        'range': {
                            'startIndex': current_index,
                            'endIndex': current_index + len(text)
                        },
                        'paragraphStyle': {
                            'namedStyleType': 'HEADING_1'
                        },
                        'fields': 'namedStyleType'
                    }
                })
                current_index += len(text) + 1
                
            elif element.name == 'h2':
                text = element.get_text(strip=True)
                requests.append({
                    'insertText': {
                        'location': {'index': current_index},
                        'text': text + '\n'
                    }
                })
                requests.append({
                    'updateParagraphStyle': {
                        'range': {
                            'startIndex': current_index,
                            'endIndex': current_index + len(text)
                        },
                        'paragraphStyle': {
                            'namedStyleType': 'HEADING_2'
                        },
                        'fields': 'namedStyleType'
                    }
                })
                current_index += len(text) + 1
                
            elif element.name == 'h3':
                text = element.get_text(strip=True)
                requests.append({
                    'insertText': {
                        'location': {'index': current_index},
                        'text': text + '\n'
                    }
                })
                requests.append({
                    'updateParagraphStyle': {
                        'range': {
                            'startIndex': current_index,
                            'endIndex': current_index + len(text)
                        },
                        'paragraphStyle': {
                            'namedStyleType': 'HEADING_3'
                        },
                        'fields': 'namedStyleType'
                    }
                })
                current_index += len(text) + 1
                
            elif element.name == 'p' and element.string:
                text = element.get_text(strip=True)
                if text:
                    requests.append({
                        'insertText': {
                            'location': {'index': current_index},
                            'text': text + '\n'
                        }
                    })
                    current_index += len(text) + 1
                    
            elif element.name == 'table':
                # 테이블 처리
                table_data = self._extract_table_data(element)
                if table_data:
                    requests.append({
                        'insertTable': {
                            'rows': len(table_data),
                            'columns': len(table_data[0]) if table_data else 0,
                            'location': {'index': current_index}
                        }
                    })
                    current_index += 1  # 테이블 추가 후 인덱스 조정
        
        return requests
    
    def _extract_table_data(self, table_element) -> List[List[str]]:
        """테이블 데이터 추출"""
        rows = []
        for tr in table_element.find_all('tr'):
            cells = []
            for cell in tr.find_all(['td', 'th']):
                cells.append(cell.get_text(strip=True))
            if cells:
                rows.append(cells)
        return rows
    
    def create_document_from_html(
        self,
        title: str,
        html_content: str,
        analysis_data: Dict[str, Any]
    ) -> Optional[Dict[str, str]]:
        """
        HTML 콘텐츠로부터 Google Docs 문서 생성
        
        Args:
            title: 문서 제목
            html_content: HTML 형식의 보고서 내용
            analysis_data: 분석 데이터
            
        Returns:
            생성된 문서 정보 (document_id, document_url)
        """
        if not self.enabled:
            print("⚠️ Google Docs 서비스가 비활성화되어 있습니다")
            return None
        
        try:
            # 1. 빈 문서 생성
            document = self.docs_service.documents().create(body={'title': title}).execute()
            document_id = document.get('documentId')
            
            print(f"📄 Google Docs 문서 생성: {title}")
            print(f"   Document ID: {document_id}")
            
            # 2. HTML을 Google Docs 형식으로 변환
            # 간단한 텍스트 변환 (HTML 태그 제거)
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 텍스트 추출 및 포맷팅
            requests = []
            current_index = 1
            
            # 제목 추가
            requests.append({
                'insertText': {
                    'location': {'index': 1},
                    'text': title + '\n\n'
                }
            })
            
            # 본문 텍스트 추가 (간소화 버전)
            # HTML의 모든 텍스트를 추출하여 삽입
            body_text = soup.get_text(separator='\n', strip=True)
            
            # 텍스트를 청크로 나누어 삽입 (API 제한 고려)
            max_length = 50000  # Google Docs API 제한
            if len(body_text) > max_length:
                body_text = body_text[:max_length] + '\n\n[나머지 내용은 원본 HTML 보고서를 참고하세요]'
            
            requests.append({
                'insertText': {
                    'location': {'index': 1 + len(title) + 2},
                    'text': body_text
                }
            })
            
            # 3. 문서 업데이트 (배치 요청)
            if requests:
                self.docs_service.documents().batchUpdate(
                    documentId=document_id,
                    body={'requests': requests}
                ).execute()
            
            # 4. 폴더로 이동 (설정된 경우)
            if self.drive_folder_id:
                self._move_to_folder(document_id, self.drive_folder_id)
            
            # 5. 공유 권한 설정 (누구나 링크를 통해 볼 수 있도록)
            self._set_public_permission(document_id)
            
            # 문서 URL 생성
            document_url = f"https://docs.google.com/document/d/{document_id}/edit"
            
            print(f"✅ Google Docs 문서 생성 완료")
            print(f"   URL: {document_url}")
            
            return {
                'document_id': document_id,
                'document_url': document_url,
                'title': title
            }
            
        except HttpError as error:
            print(f"❌ Google Docs 생성 실패: {error}")
            return None
        except Exception as e:
            print(f"❌ 예상치 못한 오류: {e}")
            return None
    
    def _move_to_folder(self, file_id: str, folder_id: str):
        """파일을 지정된 폴더로 이동"""
        try:
            # 현재 부모 폴더 가져오기
            file = self.drive_service.files().get(
                fileId=file_id,
                fields='parents'
            ).execute()
            
            previous_parents = ",".join(file.get('parents', []))
            
            # 새 폴더로 이동
            self.drive_service.files().update(
                fileId=file_id,
                addParents=folder_id,
                removeParents=previous_parents,
                fields='id, parents'
            ).execute()
            
            print(f"   📁 폴더로 이동 완료: {folder_id}")
            
        except HttpError as error:
            print(f"⚠️ 폴더 이동 실패: {error}")
    
    def _set_public_permission(self, file_id: str):
        """파일 공유 권한 설정 (링크를 통해 누구나 볼 수 있음)"""
        try:
            permission = {
                'type': 'anyone',
                'role': 'reader'
            }
            
            self.drive_service.permissions().create(
                fileId=file_id,
                body=permission
            ).execute()
            
            print(f"   🔓 공유 권한 설정 완료 (누구나 볼 수 있음)")
            
        except HttpError as error:
            print(f"⚠️ 권한 설정 실패: {error}")
    
    def save_report_to_docs(
        self,
        analysis_data: Dict[str, Any],
        html_content: str
    ) -> Optional[Dict[str, str]]:
        """
        분석 보고서를 Google Docs로 저장
        
        Args:
            analysis_data: 분석 데이터
            html_content: HTML 형식의 보고서
            
        Returns:
            문서 정보 (document_id, document_url)
        """
        if not self.enabled:
            return None
        
        # 문서 제목 생성
        address = analysis_data.get('address', '주소미상')
        unit_type = analysis_data.get('unit_type', '미지정')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        title = f"LH토지진단_{address}_{unit_type}_{timestamp}"
        
        # 문서 생성
        return self.create_document_from_html(
            title=title,
            html_content=html_content,
            analysis_data=analysis_data
        )


# 싱글톤 인스턴스
_google_docs_service = None


def get_google_docs_service() -> GoogleDocsService:
    """Google Docs 서비스 싱글톤 인스턴스 반환"""
    global _google_docs_service
    if _google_docs_service is None:
        _google_docs_service = GoogleDocsService()
    return _google_docs_service
