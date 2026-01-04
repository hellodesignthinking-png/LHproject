#!/bin/bash

# GitHub CLI를 사용한 PR 생성
# 참고: gh CLI가 설치되어 있지 않으면 웹 UI를 사용해야 합니다

echo "=========================================="
echo "Pull Request 생성 가이드"
echo "=========================================="
echo ""
echo "📋 PR 정보:"
echo "  Base Branch: main"
echo "  Head Branch: feature/expert-report-generator"
echo "  Title: ZeroSite v6.5 REAL APPRAISAL STANDARD Implementation (M2-M6)"
echo ""
echo "🔗 GitHub PR 생성 URL:"
echo "  https://github.com/hellodesignthinking-png/LHproject/compare/main...feature/expert-report-generator"
echo ""
echo "📝 PR 본문은 다음 파일을 참조하세요:"
echo "  /home/user/webapp/PR_REAL_APPRAISAL_STANDARD.md"
echo ""
echo "=========================================="
echo "자동 PR 생성 시도 중..."
echo "=========================================="
echo ""

# GitHub CLI가 있는지 확인
if command -v gh &> /dev/null; then
    echo "✅ GitHub CLI 발견. PR 생성 시도 중..."
    
    # PR 템플릿 읽기
    PR_BODY=$(cat PR_REAL_APPRAISAL_STANDARD.md)
    
    # PR 생성
    gh pr create \
        --base main \
        --head feature/expert-report-generator \
        --title "ZeroSite v6.5 REAL APPRAISAL STANDARD Implementation (M2-M6)" \
        --body "$PR_BODY" \
        --repo hellodesignthinking-png/LHproject
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Pull Request가 성공적으로 생성되었습니다!"
        gh pr list --repo hellodesignthinking-png/LHproject --head feature/expert-report-generator
    else
        echo ""
        echo "❌ PR 자동 생성 실패. 웹 UI를 사용하세요."
        echo "   URL: https://github.com/hellodesignthinking-png/LHproject/compare/main...feature/expert-report-generator"
    fi
else
    echo "⚠️  GitHub CLI (gh)가 설치되어 있지 않습니다."
    echo ""
    echo "🌐 웹 브라우저에서 PR을 생성하세요:"
    echo "   1. 다음 URL을 방문: https://github.com/hellodesignthinking-png/LHproject/compare/main...feature/expert-report-generator"
    echo "   2. 'Create pull request' 버튼 클릭"
    echo "   3. PR_REAL_APPRAISAL_STANDARD.md의 내용을 복사하여 붙여넣기"
    echo "   4. 'Create pull request' 버튼을 다시 클릭하여 완료"
    echo ""
fi

echo ""
echo "=========================================="
echo "PR 생성 프로세스 완료"
echo "=========================================="
