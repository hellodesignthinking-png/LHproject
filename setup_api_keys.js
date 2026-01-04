// ZeroSite API Keys Auto-Configuration
// 브라우저 콘솔에서 실행하세요!

console.log('🔑 ZeroSite API Keys 설정 중...');

sessionStorage.setItem('m1_api_keys', JSON.stringify({
    kakao: '1b172a21a17b8b51dd47884b45228483',
    vworld: '781864DB-126D-3B14-A0EE-1FD1B1000534',
    dataGoKr: '702ee131547fa817de152355d87249805da836374a7ffefee1c511897353807d'
}));

console.log('✅ API Keys 설정 완료!');
console.log('API Keys:', JSON.parse(sessionStorage.getItem('m1_api_keys')));
console.log('🔄 페이지를 새로고침합니다...');

// 페이지 새로고침
setTimeout(() => {
    location.reload();
}, 1000);
