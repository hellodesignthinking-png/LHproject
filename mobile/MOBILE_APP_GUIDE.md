# ZeroSite Mobile App - React Native
# 모바일 클라이언트 초기 설정 가이드

## 프로젝트 구조

```
zerosite-mobile/
├── src/
│   ├── api/                    # API 클라이언트
│   │   ├── auth.ts            # 인증 API
│   │   ├── analysis.ts        # 분석 API
│   │   └── client.ts          # Axios 설정
│   ├── components/             # 공통 컴포넌트
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Card.tsx
│   │   ├── Loading.tsx
│   │   └── Chart.tsx
│   ├── screens/                # 화면
│   │   ├── auth/
│   │   │   ├── LoginScreen.tsx
│   │   │   └── RegisterScreen.tsx
│   │   ├── dashboard/
│   │   │   └── DashboardScreen.tsx
│   │   ├── analysis/
│   │   │   ├── AnalysisInputScreen.tsx
│   │   │   ├── AnalysisProgressScreen.tsx
│   │   │   └── AnalysisResultScreen.tsx
│   │   └── comparison/
│   │       └── ComparisonScreen.tsx
│   ├── navigation/             # 내비게이션
│   │   ├── RootNavigator.tsx
│   │   ├── AuthNavigator.tsx
│   │   └── MainNavigator.tsx
│   ├── hooks/                  # 커스텀 훅
│   │   ├── useAuth.ts
│   │   ├── useAnalysis.ts
│   │   └── usePolling.ts
│   ├── store/                  # 상태 관리
│   │   ├── authStore.ts
│   │   └── analysisStore.ts
│   ├── types/                  # TypeScript 타입
│   │   ├── api.ts
│   │   ├── models.ts
│   │   └── navigation.ts
│   └── utils/                  # 유틸리티
│       ├── formatters.ts
│       └── validators.ts
├── App.tsx
├── app.json
├── package.json
└── tsconfig.json
```

## 초기 설정

### 1. 프로젝트 생성

```bash
# Expo 프로젝트 생성
npx create-expo-app zerosite-mobile --template blank-typescript
cd zerosite-mobile
```

### 2. 의존성 설치

```bash
# 네비게이션
npm install @react-navigation/native @react-navigation/stack @react-navigation/bottom-tabs
npm install react-native-screens react-native-safe-area-context

# API 통신
npm install axios react-query

# 상태 관리
npm install zustand

# 로컬 저장소
npm install @react-native-async-storage/async-storage

# UI 컴포넌트
npm install react-native-paper
npm install react-native-vector-icons

# 차트
npm install react-native-chart-kit react-native-svg

# 폼 관리
npm install react-hook-form

# 날짜/시간
npm install date-fns
```

### 3. 환경 변수 설정

`.env` 파일 생성:
```
API_BASE_URL=https://api.zerosite.com
API_TIMEOUT=30000
```

## 주요 화면 구현

### 1. 로그인 화면 (LoginScreen.tsx)

```typescript
import React, { useState } from 'react';
import { View, StyleSheet } from 'react-native';
import { TextInput, Button, Text } from 'react-native-paper';
import { useAuth } from '../hooks/useAuth';

export const LoginScreen = ({ navigation }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const { login, isLoading } = useAuth();

  const handleLogin = async () => {
    try {
      await login(username, password);
      navigation.navigate('Main');
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  return (
    <View style={styles.container}>
      <Text variant="headlineMedium">ZeroSite Login</Text>
      
      <TextInput
        label="Username"
        value={username}
        onChangeText={setUsername}
        style={styles.input}
      />
      
      <TextInput
        label="Password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
        style={styles.input}
      />
      
      <Button
        mode="contained"
        onPress={handleLogin}
        loading={isLoading}
        style={styles.button}
      >
        Login
      </Button>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    justifyContent: 'center',
  },
  input: {
    marginVertical: 10,
  },
  button: {
    marginTop: 20,
  },
});
```

### 2. 대시보드 화면 (DashboardScreen.tsx)

```typescript
import React from 'react';
import { View, FlatList, StyleSheet } from 'react-native';
import { Card, Title, Paragraph, Button } from 'react-native-paper';
import { useQuery } from 'react-query';
import { getAnalysisJobs } from '../api/analysis';

export const DashboardScreen = ({ navigation }) => {
  const { data: jobs, isLoading, refetch } = useQuery(
    'analysisJobs',
    getAnalysisJobs,
    { refetchInterval: 5000 }
  );

  const renderJob = ({ item }) => (
    <Card style={styles.card} onPress={() => navigation.navigate('Result', { jobId: item.job_id })}>
      <Card.Content>
        <Title>{item.land_info.address}</Title>
        <Paragraph>Status: {item.status}</Paragraph>
        <Paragraph>Progress: {item.progress}%</Paragraph>
      </Card.Content>
    </Card>
  );

  return (
    <View style={styles.container}>
      <Button
        mode="contained"
        onPress={() => navigation.navigate('AnalysisInput')}
        style={styles.addButton}
      >
        New Analysis
      </Button>
      
      <FlatList
        data={jobs}
        renderItem={renderJob}
        keyExtractor={(item) => item.job_id}
        refreshing={isLoading}
        onRefresh={refetch}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 10,
  },
  addButton: {
    marginBottom: 10,
  },
  card: {
    marginVertical: 5,
  },
});
```

### 3. 분석 입력 화면 (AnalysisInputScreen.tsx)

```typescript
import React from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { TextInput, Button } from 'react-native-paper';
import { useForm, Controller } from 'react-hook-form';
import { useMutation } from 'react-query';
import { createAnalysis } from '../api/analysis';

export const AnalysisInputScreen = ({ navigation }) => {
  const { control, handleSubmit } = useForm();
  const mutation = useMutation(createAnalysis);

  const onSubmit = async (data) => {
    try {
      const result = await mutation.mutateAsync(data);
      navigation.navigate('Progress', { jobId: result.job_id });
    } catch (error) {
      console.error('Analysis creation failed:', error);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Controller
        control={control}
        name="address"
        rules={{ required: true }}
        render={({ field: { onChange, value } }) => (
          <TextInput
            label="Address"
            value={value}
            onChangeText={onChange}
            style={styles.input}
          />
        )}
      />
      
      <Controller
        control={control}
        name="area_pyeong"
        rules={{ required: true }}
        render={({ field: { onChange, value } }) => (
          <TextInput
            label="Area (pyeong)"
            value={value}
            onChangeText={onChange}
            keyboardType="numeric"
            style={styles.input}
          />
        )}
      />
      
      <Controller
        control={control}
        name="asking_price_million"
        rules={{ required: true }}
        render={({ field: { onChange, value } }) => (
          <TextInput
            label="Asking Price (million won)"
            value={value}
            onChangeText={onChange}
            keyboardType="numeric"
            style={styles.input}
          />
        )}
      />
      
      <Button
        mode="contained"
        onPress={handleSubmit(onSubmit)}
        loading={mutation.isLoading}
        style={styles.button}
      >
        Start Analysis
      </Button>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
  },
  input: {
    marginVertical: 10,
  },
  button: {
    marginTop: 20,
  },
});
```

## API 클라이언트 (src/api/client.ts)

```typescript
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE_URL = 'https://api.zerosite.com';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터 (토큰 추가)
apiClient.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 응답 인터셉터 (에러 처리)
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // 토큰 만료 시 로그아웃
      await AsyncStorage.removeItem('access_token');
      // 로그인 화면으로 리다이렉트
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

## 커스텀 훅 (src/hooks/useAuth.ts)

```typescript
import { useState } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import apiClient from '../api/client';

export const useAuth = () => {
  const [isLoading, setIsLoading] = useState(false);

  const login = async (username: string, password: string) => {
    setIsLoading(true);
    try {
      const response = await apiClient.post('/api/v1/auth/login', {
        username,
        password,
      });
      
      const { access_token, refresh_token } = response.data;
      
      await AsyncStorage.setItem('access_token', access_token);
      await AsyncStorage.setItem('refresh_token', refresh_token);
      
      return response.data;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    await AsyncStorage.removeItem('access_token');
    await AsyncStorage.removeItem('refresh_token');
  };

  return { login, logout, isLoading };
};
```

## 실행

```bash
# iOS
npm run ios

# Android
npm run android

# Web
npm run web
```

## 다음 단계

1. ✅ 프로젝트 초기화
2. ✅ 기본 화면 구현
3. 📋 API 통합
4. 📋 오프라인 지원
5. 📋 푸시 알림
6. 📋 앱 스토어 배포

---

**ZeroSite Mobile App**  
**Version**: 1.0.0  
**Platform**: React Native (Expo)  
**Last Updated**: 2025-12-27
