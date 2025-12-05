"""
Google Sheets 통합 서비스
분석 결과를 Google Sheets에 저장하고 중복 검토 기능 제공
"""

import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from typing import Dict, Any, List, Optional
import os
import json


class GoogleSheetsService:
    """Google Sheets 통합 관리"""
    
    def __init__(self):
        """초기화"""
        self.credentials_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH", "./google_credentials.json")
        self.spreadsheet_id = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID", "")
        self.worksheet_name = os.getenv("GOOGLE_SHEETS_WORKSHEET_NAME", "토지분석기록")
        self.client = None
        self.spreadsheet = None
        self.worksheet = None
        
        # Google Sheets 사용 가능 여부
        self.enabled = False
        
        try:
            if os.path.exists(self.credentials_path) and self.spreadsheet_id:
                self._initialize_client()
                self.enabled = True
                print("✅ Google Sheets 연동 활성화")
            else:
                print("⚠️ Google Sheets 연동 미설정 (credentials 또는 spreadsheet_id 없음)")
        except Exception as e:
            print(f"⚠️ Google Sheets 초기화 실패: {e}")
            self.enabled = False
    
    def _initialize_client(self):
        """Google Sheets 클라이언트 초기화"""
        # OAuth2 인증 스코프 설정
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # 서비스 계정 인증
        creds = Credentials.from_service_account_file(
            self.credentials_path,
            scopes=scopes
        )
        
        # gspread 클라이언트 생성
        self.client = gspread.authorize(creds)
        
        # 스프레드시트 열기
        self.spreadsheet = self.client.open_by_key(self.spreadsheet_id)
        
        # 워크시트 가져오기 (없으면 생성)
        try:
            self.worksheet = self.spreadsheet.worksheet(self.worksheet_name)
        except gspread.exceptions.WorksheetNotFound:
            self.worksheet = self.spreadsheet.add_worksheet(
                title=self.worksheet_name,
                rows=1000,
                cols=20
            )
            self._initialize_headers()
    
    def _initialize_headers(self):
        """워크시트 헤더 초기화"""
        headers = [
            "분석일시",
            "주소",
            "지번주소",
            "토지면적(㎡)",
            "용도지역",
            "추천유형",
            "수요점수",
            "예상세대수",
            "예상층수",
            "건폐율(%)",
            "용적률(%)",
            "담당자_이름",
            "담당자_연락처",
            "담당자_부서",
            "담당자_이메일",
            "리스크개수",
            "치명적리스크",
            "LH매입제외여부",
            "보고서경로",
            "분석ID"
        ]
        
        self.worksheet.update('A1:T1', [headers])
        
        # 헤더 스타일 적용
        self.worksheet.format('A1:T1', {
            "backgroundColor": {
                "red": 0.4,
                "green": 0.49,
                "blue": 0.92
            },
            "textFormat": {
                "foregroundColor": {
                    "red": 1.0,
                    "green": 1.0,
                    "blue": 1.0
                },
                "fontSize": 10,
                "bold": True
            },
            "horizontalAlignment": "CENTER"
        })
    
    async def save_analysis(
        self,
        analysis_data: Dict[str, Any],
        consultant_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        분석 결과를 Google Sheets에 저장
        
        Args:
            analysis_data: 분석 결과 데이터
            consultant_info: 담당자 정보
            
        Returns:
            저장 결과 (row_number, duplicate_check 등)
        """
        if not self.enabled:
            return {
                "success": False,
                "message": "Google Sheets 연동이 비활성화되어 있습니다",
                "duplicate": False
            }
        
        try:
            # 중복 검사
            duplicate_info = await self.check_duplicate(
                analysis_data.get("address", ""),
                analysis_data.get("land_area", 0)
            )
            
            # 현재 시간
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 데이터 추출
            address = analysis_data.get("address", "")
            jibun_address = analysis_data.get("jibun_address", "")
            land_area = analysis_data.get("land_area", 0)
            zone_type = analysis_data.get("zone_info", {}).get("zone_type", "")
            recommended_type = analysis_data.get("recommended_unit_type", "")
            demand_score = analysis_data.get("demand_analysis", {}).get("demand_score", 0)
            
            building_capacity = analysis_data.get("building_capacity", {})
            units = building_capacity.get("units", 0)
            floors = building_capacity.get("floors", 0)
            
            zone_info = analysis_data.get("zone_info", {})
            bcr = zone_info.get("building_coverage_ratio", 0)
            far = zone_info.get("floor_area_ratio", 0)
            
            # 리스크 정보
            risks = analysis_data.get("risks", [])
            risk_count = len(risks)
            critical_risks = [r for r in risks if r.get("severity") in ["critical", "LH매입제외"]]
            critical_risk_names = ", ".join([r.get("description", "") for r in critical_risks[:3]])
            lh_excluded = any(r.get("severity") == "LH매입제외" for r in risks)
            
            # 담당자 정보
            consultant_name = ""
            consultant_phone = ""
            consultant_dept = ""
            consultant_email = ""
            
            if consultant_info:
                consultant_name = consultant_info.get("name", "")
                consultant_phone = consultant_info.get("phone", "")
                consultant_dept = consultant_info.get("department", "")
                consultant_email = consultant_info.get("email", "")
            
            # 보고서 경로 (실제로는 생성된 경로를 넣어야 함)
            report_path = analysis_data.get("report_path", "")
            
            # 분석 ID (고유 식별자)
            analysis_id = f"{now.replace(':', '').replace('-', '').replace(' ', '_')}_{hash(address) % 10000}"
            
            # 행 데이터 구성
            row_data = [
                now,
                address,
                jibun_address,
                land_area,
                zone_type,
                recommended_type,
                round(demand_score, 1),
                units,
                floors,
                bcr,
                far,
                consultant_name,
                consultant_phone,
                consultant_dept,
                consultant_email,
                risk_count,
                critical_risk_names,
                "예" if lh_excluded else "아니오",
                report_path,
                analysis_id
            ]
            
            # 시트에 추가
            self.worksheet.append_row(row_data, value_input_option='USER_ENTERED')
            
            # 추가된 행 번호 (헤더 제외)
            row_number = len(self.worksheet.get_all_values())
            
            # 중복 경고가 있으면 해당 행을 노란색으로 표시
            if duplicate_info["is_duplicate"]:
                self.worksheet.format(f'A{row_number}:T{row_number}', {
                    "backgroundColor": {
                        "red": 1.0,
                        "green": 0.95,
                        "blue": 0.8
                    }
                })
            
            return {
                "success": True,
                "row_number": row_number,
                "duplicate": duplicate_info["is_duplicate"],
                "duplicate_count": duplicate_info["count"],
                "duplicate_dates": duplicate_info["dates"],
                "analysis_id": analysis_id,
                "message": "분석 결과가 Google Sheets에 저장되었습니다"
            }
            
        except Exception as e:
            print(f"❌ Google Sheets 저장 실패: {e}")
            return {
                "success": False,
                "message": f"저장 중 오류 발생: {str(e)}",
                "duplicate": False
            }
    
    async def check_duplicate(
        self,
        address: str,
        land_area: float,
        tolerance: float = 10.0
    ) -> Dict[str, Any]:
        """
        중복 토지 검사
        
        Args:
            address: 토지 주소
            land_area: 토지 면적
            tolerance: 면적 허용 오차 (㎡)
            
        Returns:
            중복 검사 결과
        """
        if not self.enabled:
            return {
                "is_duplicate": False,
                "count": 0,
                "dates": [],
                "message": "Google Sheets 연동 비활성화"
            }
        
        try:
            # 모든 데이터 가져오기 (헤더 제외)
            all_values = self.worksheet.get_all_values()[1:]
            
            duplicates = []
            
            for row in all_values:
                if len(row) < 4:
                    continue
                
                row_date = row[0]
                row_address = row[1]
                row_land_area = float(row[3]) if row[3] else 0
                
                # 주소 유사도 검사 (간단한 포함 관계)
                address_match = address in row_address or row_address in address
                
                # 면적 유사도 검사
                area_match = abs(row_land_area - land_area) <= tolerance
                
                if address_match and area_match:
                    duplicates.append({
                        "date": row_date,
                        "address": row_address,
                        "land_area": row_land_area
                    })
            
            return {
                "is_duplicate": len(duplicates) > 0,
                "count": len(duplicates),
                "dates": [d["date"] for d in duplicates],
                "details": duplicates,
                "message": f"유사한 토지가 {len(duplicates)}건 발견되었습니다" if duplicates else "중복 없음"
            }
            
        except Exception as e:
            print(f"❌ 중복 검사 실패: {e}")
            return {
                "is_duplicate": False,
                "count": 0,
                "dates": [],
                "message": f"중복 검사 실패: {str(e)}"
            }
    
    async def get_analysis_history(
        self,
        limit: int = 100,
        consultant_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        분석 이력 조회
        
        Args:
            limit: 조회할 최대 건수
            consultant_name: 담당자 이름으로 필터링 (선택사항)
            
        Returns:
            분석 이력 리스트
        """
        if not self.enabled:
            return []
        
        try:
            all_values = self.worksheet.get_all_values()
            
            if len(all_values) < 2:
                return []
            
            headers = all_values[0]
            data_rows = all_values[1:]
            
            history = []
            
            for row in data_rows[-limit:]:  # 최근 limit개만
                if len(row) < len(headers):
                    continue
                
                record = dict(zip(headers, row))
                
                # 담당자 필터링
                if consultant_name and record.get("담당자_이름", "") != consultant_name:
                    continue
                
                history.append(record)
            
            return list(reversed(history))  # 최신순으로
            
        except Exception as e:
            print(f"❌ 이력 조회 실패: {e}")
            return []


# 싱글톤 인스턴스
_sheets_service = None


def get_sheets_service() -> GoogleSheetsService:
    """Google Sheets 서비스 싱글톤 인스턴스 반환"""
    global _sheets_service
    if _sheets_service is None:
        _sheets_service = GoogleSheetsService()
    return _sheets_service
