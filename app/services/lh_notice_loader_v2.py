"""
LH Notice Loader v2.0 - ZeroSite v7.0
Google Drive 자동 연동 + PDF 파싱 + 자동 버전 인식 + LH Rules 자동 업데이트
"""

import os
import re
import json
import io
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import asyncio
import logging

# PDF parsing
try:
    import PyPDF2
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logging.warning("PDF libraries not available. Install: pip install PyPDF2 pdfplumber")

# Google Drive API
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
    GDRIVE_AVAILABLE = True
except ImportError:
    GDRIVE_AVAILABLE = False
    logging.warning("Google Drive API not available. Install: pip install google-api-python-client google-auth")


class LHNoticeLoaderV2:
    """LH 공고문 자동 로더 v2.0 - Production Ready"""
    
    def __init__(self, storage_dir: str = "data/lh_notices", auto_update: bool = True):
        """
        Initialize LH Notice Loader v2.0
        
        Args:
            storage_dir: PDF 및 JSON 저장 디렉토리
            auto_update: 자동 LH Rules 업데이트 활성화
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.auto_rules_dir = Path("data/lh_rules_auto")
        self.auto_rules_dir.mkdir(parents=True, exist_ok=True)
        
        self.history_file = self.storage_dir / "processing_history_v2.json"
        self.auto_update = auto_update
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Google Drive 설정
        self.drive_folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "13luANIq_cQ7KbzxVqb4QyG2r_q8-KaVv")
        self.credentials_path = os.getenv("GOOGLE_DRIVE_CREDENTIALS_PATH", "credentials/google-drive-credentials.json")
        
        # v2.0 향상된 파일명 패턴 (다양한 형식 지원)
        self.filename_patterns = [
            # 패턴 1: 서울25-8차민간신축매입약정방식공고문.pdf
            r"(?P<region>[가-힣]+)(?P<year>\d{2,4})-(?P<round>\d+)차",
            # 패턴 2: 경기24-3차_공고문_최종.pdf
            r"(?P<region>[가-힣]+)(?P<year>\d{2,4})-(?P<round>\d+)차.*공고",
            # 패턴 3: 부산_2025_12차_공고.pdf
            r"(?P<region>[가-힣]+)_(?P<year>\d{4})_(?P<round>\d+)차",
            # 패턴 4: LH_서울_2025년_3차_공고.pdf
            r"LH[_]?(?P<region>[가-힣]+)[_]?(?P<year>\d{4})년?[_]?(?P<round>\d+)차",
            # 패턴 5: 2025-서울-3차.pdf
            r"(?P<year>\d{4})-(?P<region>[가-힣]+)-(?P<round>\d+)차",
        ]
        
        # LH 규칙 추출 키워드
        self.rule_keywords = {
            "location": ["입지조건", "역세권", "학교", "교통", "접근성"],
            "building": ["건축", "층수", "세대", "면적", "구조"],
            "eligibility": ["신청자격", "소득", "자산", "우선순위"],
            "price": ["임대료", "보증금", "가격", "금액"],
            "scoring": ["배점", "점수", "평가", "기준"],
            "requirements": ["필수", "요구사항", "조건", "기준"]
        }
    
    def _normalize_year(self, year_str: str) -> int:
        """연도 정규화 (2자리 → 4자리)"""
        year = int(year_str)
        if year < 100:
            year += 2000
        return year
    
    def parse_filename(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        파일명에서 정보 추출 (v2.0 enhanced with multiple patterns)
        
        Args:
            filename: PDF 파일명
            
        Returns:
            추출된 정보 (region, year, round, version_id) 또는 None
        """
        for pattern in self.filename_patterns:
            match = re.search(pattern, filename)
            if match:
                groups = match.groupdict()
                year = self._normalize_year(groups["year"])
                round_num = groups["round"]
                region = groups.get("region", "전국")
                
                return {
                    "region": region,
                    "year": year,
                    "round": f"{round_num}차",
                    "version_id": f"{region}_{year}_{round_num}차",
                    "filename": filename,
                    "parsed_at": datetime.now().isoformat()
                }
        
        self.logger.warning(f"Could not parse filename: {filename}")
        return None
    
    async def sync_from_drive(self, force_resync: bool = False) -> Dict[str, Any]:
        """
        Google Drive에서 LH 공고문 동기화 (v2.0 production-ready)
        
        Args:
            force_resync: True면 이미 처리한 파일도 재처리
            
        Returns:
            동기화 결과 {status, synced_files, new_versions, failed_files}
        """
        if not GDRIVE_AVAILABLE:
            return {
                "status": "error",
                "message": "Google Drive API not available. Install google-api-python-client",
                "synced_files": 0,
                "new_versions": [],
                "failed_files": []
            }
        
        try:
            # Validate credentials
            if not os.path.exists(self.credentials_path):
                self.logger.error(f"Credentials not found at: {self.credentials_path}")
                return {
                    "status": "error",
                    "message": f"Google Drive credentials not found at {self.credentials_path}. " +
                               "Set GOOGLE_DRIVE_CREDENTIALS_PATH environment variable.",
                    "synced_files": 0,
                    "new_versions": [],
                    "failed_files": []
                }
            
            # Initialize Google Drive API
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=['https://www.googleapis.com/auth/drive.readonly']
            )
            
            service = build('drive', 'v3', credentials=credentials)
            
            # Query PDF files from Drive folder
            query = f"'{self.drive_folder_id}' in parents and mimeType='application/pdf' and trashed=false"
            results = service.files().list(
                q=query,
                fields="files(id, name, modifiedTime, size)",
                orderBy="modifiedTime desc",
                pageSize=100
            ).execute()
            
            files = results.get('files', [])
            
            if not files:
                self.logger.info("No PDF files found in Google Drive folder")
                return {
                    "status": "success",
                    "message": "No PDF files found in Drive folder",
                    "synced_files": 0,
                    "new_versions": [],
                    "failed_files": []
                }
            
            self.logger.info(f"Found {len(files)} PDF files in Google Drive")
            
            # Load processing history
            history = self._load_processing_history()
            
            synced_count = 0
            new_versions = []
            failed_files = []
            
            for file in files:
                file_id = file['id']
                filename = file['name']
                file_size = file.get('size', 0)
                
                self.logger.info(f"Processing: {filename} ({file_size} bytes)")
                
                # Parse filename
                file_info = self.parse_filename(filename)
                if not file_info:
                    self.logger.warning(f"Unrecognized filename format: {filename}")
                    failed_files.append({
                        "filename": filename,
                        "reason": "Unrecognized filename format",
                        "suggestions": "Use format like: 서울25-8차공고문.pdf or 경기_2025_3차.pdf"
                    })
                    continue
                
                # Check if already processed
                if not force_resync and filename in history.get("processed_files", []):
                    self.logger.info(f"Already processed: {filename}")
                    continue
                
                try:
                    # Download PDF from Google Drive
                    self.logger.info(f"Downloading: {filename}")
                    
                    request = service.files().get_media(fileId=file_id)
                    pdf_path = self.storage_dir / filename
                    
                    fh = io.BytesIO()
                    downloader = MediaIoBaseDownload(fh, request)
                    
                    done = False
                    while not done:
                        status, done = downloader.next_chunk()
                        if status:
                            progress = int(status.progress() * 100)
                            self.logger.info(f"Download progress: {progress}%")
                    
                    # Save PDF file
                    with open(pdf_path, 'wb') as f:
                        f.write(fh.getvalue())
                    
                    self.logger.info(f"Downloaded successfully: {pdf_path}")
                    
                    # Parse PDF and extract rules
                    rules = await self.process_notice_file(str(pdf_path), file_info)
                    
                    if rules and rules.get("success"):
                        new_versions.append(file_info["version_id"])
                        synced_count += 1
                        
                        # Save to auto rules directory
                        if self.auto_update:
                            await self._save_auto_rules(rules, file_info)
                        
                        # Update history
                        history.setdefault("processed_files", []).append(filename)
                        history.setdefault("versions", []).append({
                            "version_id": file_info["version_id"],
                            "filename": filename,
                            "processed_at": datetime.now().isoformat(),
                            "rules_count": len(rules.get("rules", {})),
                            "file_size": file_size
                        })
                        
                        self.logger.info(f"Successfully processed: {filename} -> {file_info['version_id']}")
                    else:
                        raise Exception("Rule extraction failed or returned no data")
                    
                except Exception as e:
                    self.logger.error(f"Failed to process: {filename} - {e}")
                    failed_files.append({
                        "filename": filename,
                        "reason": str(e),
                        "timestamp": datetime.now().isoformat()
                    })
            
            # Save processing history
            self._save_processing_history(history)
            
            result = {
                "status": "success",
                "synced_files": synced_count,
                "new_versions": new_versions,
                "failed_files": failed_files,
                "total_files": len(files),
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"Sync completed: {synced_count}/{len(files)} files processed")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Sync failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "synced_files": 0,
                "new_versions": [],
                "failed_files": []
            }
    
    async def process_notice_file(self, pdf_path: str, file_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        PDF 공고문 파싱 및 규칙 추출 (v2.0 enhanced)
        
        Args:
            pdf_path: PDF 파일 경로
            file_info: 파일 정보 (region, year, round, version_id)
            
        Returns:
            추출된 규칙 데이터 또는 None
        """
        if not PDF_AVAILABLE:
            self.logger.error("PDF parsing libraries not available")
            return None
        
        try:
            self.logger.info(f"Parsing PDF: {pdf_path}")
            
            # Extract text from PDF
            text_content = await self._extract_pdf_text(pdf_path)
            
            if not text_content:
                self.logger.warning("No text extracted from PDF")
                return None
            
            # Extract rules using keyword matching and pattern recognition
            rules = self._extract_rules_from_text(text_content, file_info)
            
            # Structure the rules data
            structured_rules = {
                "success": True,
                "version_id": file_info["version_id"],
                "region": file_info["region"],
                "year": file_info["year"],
                "round": file_info["round"],
                "filename": file_info["filename"],
                "parsed_at": datetime.now().isoformat(),
                "rules": rules,
                "metadata": {
                    "text_length": len(text_content),
                    "rules_count": len(rules),
                    "extraction_method": "keyword_pattern_matching_v2"
                }
            }
            
            # Save JSON output
            json_path = self.storage_dir / f"{file_info['version_id']}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(structured_rules, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Rules extracted and saved: {json_path}")
            
            return structured_rules
            
        except Exception as e:
            self.logger.error(f"Failed to process notice file: {e}")
            return None
    
    async def _extract_pdf_text(self, pdf_path: str) -> str:
        """PDF에서 텍스트 추출"""
        text_content = ""
        
        try:
            # Try pdfplumber first (better for tables and formatted text)
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        text_content += f"\n--- Page {page_num} ---\n{page_text}"
                        
        except Exception as e:
            self.logger.warning(f"pdfplumber failed, trying PyPDF2: {e}")
            
            try:
                # Fallback to PyPDF2
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page_num in range(len(pdf_reader.pages)):
                        page = pdf_reader.pages[page_num]
                        text_content += f"\n--- Page {page_num + 1} ---\n{page.extract_text()}"
                        
            except Exception as e2:
                self.logger.error(f"PyPDF2 also failed: {e2}")
                return ""
        
        return text_content
    
    def _extract_rules_from_text(self, text: str, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        텍스트에서 LH 규칙 추출 (v2.0 with intelligent pattern matching)
        """
        rules = {}
        
        # Extract location rules
        rules["location"] = self._extract_location_rules(text)
        
        # Extract building rules
        rules["building"] = self._extract_building_rules(text)
        
        # Extract eligibility rules
        rules["eligibility"] = self._extract_eligibility_rules(text)
        
        # Extract pricing rules
        rules["pricing"] = self._extract_pricing_rules(text)
        
        # Extract scoring rules
        rules["scoring"] = self._extract_scoring_rules(text)
        
        # Extract general requirements
        rules["requirements"] = self._extract_requirements(text)
        
        return rules
    
    def _extract_location_rules(self, text: str) -> Dict[str, Any]:
        """입지조건 규칙 추출"""
        rules = {}
        
        # Extract subway distance rules
        subway_pattern = r"역세권.*?(\d+)m?.*?이내"
        subway_match = re.search(subway_pattern, text)
        if subway_match:
            rules["subway_distance"] = int(subway_match.group(1))
        
        # Extract school distance rules
        school_pattern = r"(?:초등학교|학교).*?(\d+)m?.*?이내"
        school_match = re.search(school_pattern, text)
        if school_match:
            rules["school_distance"] = int(school_match.group(1))
        
        return rules
    
    def _extract_building_rules(self, text: str) -> Dict[str, Any]:
        """건축 규칙 추출"""
        rules = {}
        
        # Extract floor rules
        floor_pattern = r"(?:층수|높이).*?(\d+)(?:층|개층)"
        floor_match = re.search(floor_pattern, text)
        if floor_match:
            rules["max_floors"] = int(floor_match.group(1))
        
        # Extract unit count rules
        unit_pattern = r"(?:세대|가구).*?(\d+)(?:세대|가구)"
        unit_match = re.search(unit_pattern, text)
        if unit_match:
            rules["min_units"] = int(unit_match.group(1))
        
        return rules
    
    def _extract_eligibility_rules(self, text: str) -> Dict[str, Any]:
        """신청자격 규칙 추출"""
        rules = {}
        
        # Extract income rules
        income_pattern = r"소득.*?(\d+)%"
        income_match = re.search(income_pattern, text)
        if income_match:
            rules["income_limit"] = int(income_match.group(1))
        
        return rules
    
    def _extract_pricing_rules(self, text: str) -> Dict[str, Any]:
        """가격 규칙 추출"""
        rules = {}
        
        # Extract deposit rules
        deposit_pattern = r"보증금.*?(\d+(?:,\d+)*)"
        deposit_match = re.search(deposit_pattern, text)
        if deposit_match:
            rules["deposit_limit"] = deposit_match.group(1)
        
        return rules
    
    def _extract_scoring_rules(self, text: str) -> Dict[str, Any]:
        """배점 규칙 추출"""
        rules = {}
        
        # Extract scoring criteria
        scoring_pattern = r"(?:배점|점수).*?(\d+)점"
        scoring_matches = re.findall(scoring_pattern, text)
        if scoring_matches:
            rules["total_points"] = sum(int(m) for m in scoring_matches[:10])  # Limit to first 10
        
        return rules
    
    def _extract_requirements(self, text: str) -> List[str]:
        """일반 요구사항 추출"""
        requirements = []
        
        # Extract bullet points and numbered lists
        bullet_pattern = r"[•\-\*]\s*([^\n]+)"
        requirements.extend(re.findall(bullet_pattern, text))
        
        return requirements[:20]  # Limit to 20 requirements
    
    async def _save_auto_rules(self, rules: Dict[str, Any], file_info: Dict[str, Any]):
        """자동 추출된 규칙을 LH Rules 파일로 저장"""
        auto_rules_path = self.auto_rules_dir / f"LH_rules_auto_{file_info['version_id']}.json"
        
        # Convert to LH Rules format
        lh_rules_format = {
            "version": file_info["version_id"],
            "updated_at": datetime.now().isoformat(),
            "source": file_info["filename"],
            "rules": rules["rules"],
            "auto_generated": True
        }
        
        with open(auto_rules_path, 'w', encoding='utf-8') as f:
            json.dump(lh_rules_format, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Auto rules saved: {auto_rules_path}")
    
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
    
    async def list_versions(self) -> List[Dict[str, Any]]:
        """처리된 모든 버전 목록 반환"""
        history = self._load_processing_history()
        return history.get("versions", [])
    
    async def get_latest_rules(self) -> Optional[Dict[str, Any]]:
        """최신 LH 규칙 반환"""
        versions = await self.list_versions()
        if not versions:
            return None
        
        latest_version = versions[-1]
        rules_file = self.auto_rules_dir / f"LH_rules_auto_{latest_version['version_id']}.json"
        
        if rules_file.exists():
            with open(rules_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return None


# Async test function
async def test_lh_notice_loader_v2():
    """Test LH Notice Loader v2.0"""
    loader = LHNoticeLoaderV2()
    
    print("=== LH Notice Loader v2.0 Test ===\n")
    
    # Test filename parsing
    test_filenames = [
        "서울25-8차민간신축매입약정방식공고문.pdf",
        "경기24-3차_공고문_최종.pdf",
        "부산_2025_12차_공고.pdf",
        "LH_서울_2025년_3차_공고.pdf",
        "2025-서울-3차.pdf"
    ]
    
    print("1. Filename Parsing Test:")
    for filename in test_filenames:
        result = loader.parse_filename(filename)
        print(f"   {filename}")
        print(f"   → {result}\n")
    
    # Test sync from Google Drive
    print("\n2. Google Drive Sync Test:")
    sync_result = await loader.sync_from_drive()
    print(f"   Status: {sync_result['status']}")
    print(f"   Synced: {sync_result['synced_files']} files")
    print(f"   New versions: {sync_result['new_versions']}")
    if sync_result['failed_files']:
        print(f"   Failed: {len(sync_result['failed_files'])} files")
    
    # Test list versions
    print("\n3. List Versions:")
    versions = await loader.list_versions()
    print(f"   Total versions: {len(versions)}")
    for v in versions[:5]:  # Show first 5
        print(f"   - {v['version_id']}: {v['rules_count']} rules")
    
    # Test get latest rules
    print("\n4. Latest Rules:")
    latest = await loader.get_latest_rules()
    if latest:
        print(f"   Version: {latest['version']}")
        print(f"   Rules: {len(latest.get('rules', {}))} categories")
    else:
        print("   No rules available")
    
    print("\n=== Test Complete ===")


if __name__ == "__main__":
    asyncio.run(test_lh_notice_loader_v2())
