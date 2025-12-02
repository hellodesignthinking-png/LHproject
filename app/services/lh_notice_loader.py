"""
LH Notice Loader - ZeroSite Land Report v5.0
Google Drive에서 LH 공고문 PDF를 자동으로 다운로드하고 규칙 추출
"""

import os
import re
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import asyncio


class LHNoticeLoader:
    """LH 공고문 자동 로더 (Google Drive 연동)"""
    
    def __init__(self, storage_dir: str = "data/lh_notices"):
        """
        초기화
        
        Args:
            storage_dir: PDF 및 JSON 저장 디렉토리
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.auto_rules_dir = Path("data/lh_rules_auto")
        self.auto_rules_dir.mkdir(parents=True, exist_ok=True)
        
        self.history_file = self.storage_dir / "processing_history.json"
        
        # Google Drive 설정
        self.drive_folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "13luANIq_cQ7KbzxVqb4QyG2r_q8-KaVv")
        self.credentials_path = os.getenv("GOOGLE_DRIVE_CREDENTIALS_PATH", "")
        
        # v2.0 파일명 패턴 (더 유연한 패턴)
        self.filename_patterns = [
            # 패턴 1: 서울25-8차민간신축매입약정방식공고문.pdf
            r"(?P<region>[가-힣]+)(?P<year>\d{2,4})-(?P<round>\d+)차",
            # 패턴 2: 경기24-3차_공고문_최종.pdf
            r"(?P<region>[가-힣]+)(?P<year>\d{2,4})-(?P<round>\d+)차.*공고",
            # 패턴 3: 부산_2025_12차_공고.pdf
            r"(?P<region>[가-힣]+)_(?P<year>\d{4})_(?P<round>\d+)차",
        ]
        
    def _normalize_year(self, year_str: str) -> int:
        """연도 정규화 (2자리 → 4자리)"""
        year = int(year_str)
        if year < 100:
            year += 2000
        return year
    
    def parse_filename(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        파일명에서 정보 추출 (v2.0 improved)
        
        Args:
            filename: PDF 파일명
            
        Returns:
            추출된 정보 (region, year, round) 또는 None
        """
        for pattern in self.filename_patterns:
            match = re.search(pattern, filename)
            if match:
                groups = match.groupdict()
                year = self._normalize_year(groups["year"])
                round_num = groups["round"]
                
                return {
                    "region": groups["region"],
                    "year": year,
                    "round": f"{round_num}차",
                    "version_id": f"{year}_{round_num}차",
                    "filename": filename
                }
        
        return None
    
    async def sync_from_drive(self) -> Dict[str, Any]:
        """
        Google Drive에서 LH 공고문 동기화
        
        Returns:
            동기화 결과 (synced_files, new_versions, failed_files)
        """
        try:
            # Google Drive API 클라이언트 초기화
            if not self.credentials_path or not os.path.exists(self.credentials_path):
                return {
                    "status": "error",
                    "message": "Google Drive credentials not configured. Set GOOGLE_DRIVE_CREDENTIALS_PATH environment variable.",
                    "synced_files": 0,
                    "new_versions": [],
                    "failed_files": []
                }
            
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaIoBaseDownload
            import io
            
            # 인증
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=['https://www.googleapis.com/auth/drive.readonly']
            )
            
            service = build('drive', 'v3', credentials=credentials)
            
            # 폴더 내 PDF 파일 목록 가져오기
            query = f"'{self.drive_folder_id}' in parents and mimeType='application/pdf' and trashed=false"
            results = service.files().list(
                q=query,
                fields="files(id, name, modifiedTime)",
                orderBy="modifiedTime desc"
            ).execute()
            
            files = results.get('files', [])
            
            if not files:
                return {
                    "status": "success",
                    "message": "No PDF files found in Drive folder",
                    "synced_files": 0,
                    "new_versions": [],
                    "failed_files": []
                }
            
            # 처리 이력 로드
            history = self._load_processing_history()
            
            synced_count = 0
            new_versions = []
            failed_files = []
            
            for file in files:
                file_id = file['id']
                filename = file['name']
                
                # 파일명 파싱
                file_info = self.parse_filename(filename)
                if not file_info:
                    print(f"⚠️ 파일명 형식을 인식할 수 없음: {filename}")
                    failed_files.append({"filename": filename, "reason": "Unrecognized filename format"})
                    continue
                
                # 이미 처리한 파일인지 확인
                if filename in history.get("processed_files", []):
                    print(f"⏭️  이미 처리됨: {filename}")
                    continue
                
                try:
                    print(f"📥 다운로드 중: {filename}")
                    
                    # PDF 다운로드
                    request = service.files().get_media(fileId=file_id)
                    pdf_path = self.storage_dir / filename
                    
                    fh = io.BytesIO()
                    downloader = MediaIoBaseDownload(fh, request)
                    
                    done = False
                    while not done:
                        status, done = downloader.next_chunk()
                    
                    # 파일 저장
                    with open(pdf_path, 'wb') as f:
                        f.write(fh.getvalue())
                    
                    print(f"✅ 다운로드 완료: {pdf_path}")
                    
                    # PDF에서 규칙 추출
                    rules = await self.process_notice_file(str(pdf_path), file_info)
                    
                    if rules:
                        new_versions.append(file_info["version_id"])
                        synced_count += 1
                        
                        # 처리 이력에 추가
                        history.setdefault("processed_files", []).append(filename)
                        history.setdefault("versions", []).append({
                            "version_id": file_info["version_id"],
                            "filename": filename,
                            "processed_at": datetime.now().isoformat(),
                            "rules_count": len(rules.get("rules", {}))
                        })
                    
                except Exception as e:
                    print(f"❌ 처리 실패: {filename} - {e}")
                    failed_files.append({"filename": filename, "reason": str(e)})
            
            # 처리 이력 저장
            self._save_processing_history(history)
            
            return {
                "status": "success",
                "synced_files": synced_count,
                "new_versions": new_versions,
                "failed_files": failed_files,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "synced_files": 0,
                "new_versions": [],
                "failed_files": []
            }
    
    async def process_notice_file(
        self, 
        pdf_path: str, 
        file_info: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        PDF 파일에서 LH 규칙 추출 및 JSON 생성
        
        Args:
            pdf_path: PDF 파일 경로
            file_info: 파일 정보 (region, year, round)
            
        Returns:
            추출된 규칙 또는 None
        """
        try:
            # PDF에서 텍스트 추출
            text = self._extract_text_from_pdf(pdf_path)
            if not text:
                print(f"⚠️ PDF에서 텍스트를 추출할 수 없음: {pdf_path}")
                return None
            
            # 규칙 추출
            rules = self._extract_rules_from_text(text, file_info)
            
            # JSON 저장
            json_path = self.auto_rules_dir / f"{file_info['version_id']}.json"
            self._save_rules_to_json(rules, json_path)
            
            print(f"✅ 규칙 추출 완료: {json_path}")
            
            # Version Manager에 등록 (선택사항)
            # self._register_with_version_manager(file_info["version_id"], str(json_path))
            
            return rules
            
        except Exception as e:
            print(f"❌ PDF 처리 오류: {pdf_path} - {e}")
            return None
    
    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """PDF에서 텍스트 추출"""
        try:
            import pdfplumber
            
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
            
            return text
            
        except ImportError:
            print("⚠️ pdfplumber가 설치되지 않았습니다. pip install pdfplumber")
            return ""
        except Exception as e:
            print(f"⚠️ PDF 텍스트 추출 실패: {e}")
            return ""
    
    def _extract_rules_from_text(
        self, 
        text: str, 
        file_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """텍스트에서 LH 규칙 추출"""
        rules = {
            "version": file_info["version_id"],
            "region": file_info["region"],
            "year": file_info["year"],
            "round": file_info["round"],
            "effective_date": f"{file_info['year']}-01-01",  # 기본값
            "rules": {},
            "source_file": file_info["filename"],
            "parsed_at": datetime.now().isoformat(),
            "parser_version": "v5.0"
        }
        
        # 주거 유형 패턴
        housing_types = ["청년", "신혼·신생아", "다자녀", "고령자", "일반", "든든전세"]
        
        for housing_type in housing_types:
            # 해당 유형 관련 텍스트 찾기
            type_pattern = rf"{housing_type}.*?(\d+)평?㎡?\s*이상"
            matches = re.finditer(type_pattern, text, re.IGNORECASE)
            
            for match in matches:
                area_str = match.group(1)
                
                try:
                    min_area = float(area_str.replace(',', ''))
                    
                    rules["rules"][housing_type] = {
                        "min_land_area_sqm": min_area,
                        "max_unit_area_sqm": self._get_default_unit_area(housing_type),
                        "criteria": [
                            f"{housing_type} 유형 기준",
                            f"최소 토지면적: {min_area}㎡"
                        ]
                    }
                    
                    break  # 첫 번째 매치만 사용
                    
                except ValueError:
                    continue
        
        return rules
    
    def _get_default_unit_area(self, housing_type: str) -> float:
        """유형별 기본 전용면적 (㎡)"""
        defaults = {
            "청년": 40,
            "신혼·신생아": 60,
            "다자녀": 85,
            "고령자": 40,
            "일반": 85,
            "든든전세": 85
        }
        return defaults.get(housing_type, 60)
    
    def _save_rules_to_json(self, rules: Dict[str, Any], json_path: Path):
        """규칙을 JSON 파일로 저장"""
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(rules, f, ensure_ascii=False, indent=2)
        
        print(f"💾 JSON 저장됨: {json_path}")
    
    def _load_processing_history(self) -> Dict[str, Any]:
        """처리 이력 로드"""
        if self.history_file.exists():
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_processing_history(self, history: Dict[str, Any]):
        """처리 이력 저장"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    
    def list_processed_notices(self) -> List[Dict[str, Any]]:
        """처리된 공고문 목록 반환"""
        history = self._load_processing_history()
        return history.get("versions", [])
    
    def get_notice_rules(self, version_id: str) -> Optional[Dict[str, Any]]:
        """특정 버전의 규칙 가져오기"""
        json_path = self.auto_rules_dir / f"{version_id}.json"
        
        if json_path.exists():
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return None


# 전역 인스턴스
_notice_loader = None

def get_notice_loader() -> LHNoticeLoader:
    """Notice Loader 싱글톤 인스턴스 반환"""
    global _notice_loader
    if _notice_loader is None:
        _notice_loader = LHNoticeLoader()
    return _notice_loader
