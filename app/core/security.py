"""
ZeroSite v4.0 Security Module
==============================

JWT 인증, API 키 관리, 비밀번호 해싱

Author: ZeroSite Security Team
Date: 2025-12-27
Version: 1.0
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
import secrets
import hashlib
from pydantic import BaseModel


# Security Configuration
SECRET_KEY = "zerosite-secret-key-change-in-production-use-env-variable"  # 프로덕션에서는 환경변수 사용!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
API_KEY_LENGTH = 32

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ==================== Pydantic Models ====================

class Token(BaseModel):
    """토큰 응답 모델"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """토큰 데이터 모델"""
    user_id: Optional[str] = None
    username: Optional[str] = None
    scopes: list = []


class User(BaseModel):
    """사용자 모델"""
    user_id: str
    username: str
    email: str
    full_name: Optional[str] = None
    disabled: bool = False
    is_admin: bool = False


class UserInDB(User):
    """DB 저장용 사용자 모델"""
    hashed_password: str


class APIKeyInDB(BaseModel):
    """API 키 모델"""
    key_id: str
    api_key_hash: str
    user_id: str
    name: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool = True
    usage_count: int = 0
    last_used: Optional[datetime] = None


# ==================== Password Functions ====================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호 검증"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """비밀번호 해싱"""
    return pwd_context.hash(password)


# ==================== JWT Token Functions ====================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    JWT Access Token 생성
    
    Args:
        data: 토큰에 포함할 데이터
        expires_delta: 만료 시간 (기본: 30분)
        
    Returns:
        JWT 토큰 문자열
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    JWT Refresh Token 생성
    
    Args:
        data: 토큰에 포함할 데이터
        
    Returns:
        JWT Refresh 토큰 문자열
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    JWT 토큰 디코딩
    
    Args:
        token: JWT 토큰 문자열
        
    Returns:
        토큰 페이로드
        
    Raises:
        JWTError: 토큰이 유효하지 않을 경우
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise JWTError(f"Invalid token: {str(e)}")


def verify_token(token: str, token_type: str = "access") -> Optional[TokenData]:
    """
    토큰 검증
    
    Args:
        token: JWT 토큰 문자열
        token_type: 토큰 유형 ("access" or "refresh")
        
    Returns:
        TokenData 또는 None
    """
    try:
        payload = decode_token(token)
        
        # 토큰 타입 확인
        if payload.get("type") != token_type:
            return None
        
        user_id: str = payload.get("sub")
        username: str = payload.get("username")
        scopes: list = payload.get("scopes", [])
        
        if user_id is None:
            return None
        
        return TokenData(user_id=user_id, username=username, scopes=scopes)
        
    except JWTError:
        return None


# ==================== API Key Functions ====================

def generate_api_key() -> str:
    """
    API 키 생성
    
    Returns:
        32자리 랜덤 API 키 (예: zerosite_1234567890abcdef...)
    """
    random_part = secrets.token_urlsafe(API_KEY_LENGTH)
    return f"zerosite_{random_part[:API_KEY_LENGTH]}"


def hash_api_key(api_key: str) -> str:
    """
    API 키 해싱 (저장용)
    
    Args:
        api_key: 원본 API 키
        
    Returns:
        SHA256 해시
    """
    return hashlib.sha256(api_key.encode()).hexdigest()


def verify_api_key(api_key: str, api_key_hash: str) -> bool:
    """
    API 키 검증
    
    Args:
        api_key: 검증할 API 키
        api_key_hash: 저장된 해시
        
    Returns:
        검증 성공 여부
    """
    return hash_api_key(api_key) == api_key_hash


# ==================== Mock User Database ====================
# 프로덕션에서는 실제 데이터베이스로 교체

fake_users_db = {
    "admin": UserInDB(
        user_id="user_001",
        username="admin",
        email="admin@zerosite.com",
        full_name="Admin User",
        hashed_password=get_password_hash("admin123"),
        disabled=False,
        is_admin=True
    ),
    "demo": UserInDB(
        user_id="user_002",
        username="demo",
        email="demo@zerosite.com",
        full_name="Demo User",
        hashed_password=get_password_hash("demo123"),
        disabled=False,
        is_admin=False
    )
}

fake_api_keys_db: Dict[str, APIKeyInDB] = {}


def get_user(username: str) -> Optional[UserInDB]:
    """사용자 조회"""
    return fake_users_db.get(username)


def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    """
    사용자 인증
    
    Args:
        username: 사용자명
        password: 비밀번호
        
    Returns:
        인증된 사용자 또는 None
    """
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_user_api_key(user_id: str, key_name: str, expires_days: Optional[int] = None) -> tuple[str, APIKeyInDB]:
    """
    사용자 API 키 생성
    
    Args:
        user_id: 사용자 ID
        key_name: API 키 이름
        expires_days: 만료 기간 (일)
        
    Returns:
        (원본 API 키, APIKeyInDB)
    """
    api_key = generate_api_key()
    api_key_hash = hash_api_key(api_key)
    
    key_id = f"key_{secrets.token_hex(8)}"
    
    expires_at = None
    if expires_days:
        expires_at = datetime.utcnow() + timedelta(days=expires_days)
    
    api_key_data = APIKeyInDB(
        key_id=key_id,
        api_key_hash=api_key_hash,
        user_id=user_id,
        name=key_name,
        created_at=datetime.utcnow(),
        expires_at=expires_at,
        is_active=True,
        usage_count=0,
        last_used=None
    )
    
    fake_api_keys_db[key_id] = api_key_data
    
    return api_key, api_key_data


def verify_api_key_access(api_key: str) -> Optional[APIKeyInDB]:
    """
    API 키 접근 검증
    
    Args:
        api_key: 원본 API 키
        
    Returns:
        APIKeyInDB 또는 None
    """
    api_key_hash = hash_api_key(api_key)
    
    for key_data in fake_api_keys_db.values():
        if not key_data.is_active:
            continue
        
        if key_data.expires_at and key_data.expires_at < datetime.utcnow():
            continue
        
        if verify_api_key(api_key, key_data.api_key_hash):
            # 사용 기록 업데이트
            key_data.usage_count += 1
            key_data.last_used = datetime.utcnow()
            return key_data
    
    return None


# ==================== Utility Functions ====================

def get_current_user_from_token(token: str) -> Optional[User]:
    """
    토큰에서 현재 사용자 추출
    
    Args:
        token: JWT 토큰
        
    Returns:
        User 또는 None
    """
    token_data = verify_token(token)
    if not token_data:
        return None
    
    user = get_user(token_data.username)
    if not user:
        return None
    
    return User(**user.dict())


# 초기 테스트 API 키 생성
if not fake_api_keys_db:
    # Admin용 테스트 API 키
    test_key, _ = create_user_api_key("user_001", "Admin Test Key", expires_days=365)
    print(f"🔑 Admin Test API Key: {test_key}")
    
    # Demo용 테스트 API 키
    demo_key, _ = create_user_api_key("user_002", "Demo Test Key", expires_days=30)
    print(f"🔑 Demo Test API Key: {demo_key}")
