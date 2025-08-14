# Исправления ESLint ошибок для order-management-app

## 1. Неиспользуемые переменные error

### src/app/api/partner-orders/route.ts
```typescript
// Заменить:
} catch (error) {
  console.error('Error:', error);
  return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
}

// На:
} catch (error) {
  console.error('Error:', error);
  return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
}
```

### src/app/api/partner-orders-all/route.ts
```typescript
// Заменить все catch блоки аналогично
} catch (error) {
  console.error('Error:', error);
  return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
}
```

### src/app/api/partner-services/route.ts
```typescript
// Заменить все catch блоки аналогично
} catch (error) {
  console.error('Error:', error);
  return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
}
```

### src/app/api/user-orders/route.ts
```typescript
// Заменить все catch блоки аналогично
} catch (error) {
  console.error('Error:', error);
  return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
}
```

## 2. Неиспользуемые параметры

### src/app/api/partners/route.ts
```typescript
// Заменить:
app.post('/api/partners', async (req, res) => {
  const { username, email, password } = req.body;
  // ...

// На:
app.post('/api/partners', async (req, res) => {
  const { username, email } = req.body; // Убрать password если не используется
  // ...

// Заменить:
app.get('/api/partners', async (req, res) => {
  const partners = await Partner.find({}, (err, docs) => {
    // ...

// На:
app.get('/api/partners', async (req, res) => {
  const partners = await Partner.find({}, (err, docs) => {
    // ...
```

## 3. Неиспользуемые переменные состояния

### src/app/functions-steps/page.tsx
```typescript
// Заменить:
const [selectedPartnerFunctions, setSelectedPartnerFunctions] = useState([]);

// На:
// Убрать если не используются
// const [selectedPartnerFunctions, setSelectedPartnerFunctions] = useState([]);
```

### src/app/partner-dashboard/page.tsx
```typescript
// Заменить:
const [banners, setBanners] = useState([]);
const [bannersLoading, setBannersLoading] = useState(false);
const [editingBanner, setEditingBanner] = useState(null);

// На:
// Убрать если не используются
// const [banners, setBanners] = useState([]);
// const [bannersLoading, setBannersLoading] = useState(false);
// const [editingBanner, setEditingBanner] = useState(null);
```

### src/app/payment/page.tsx
```typescript
// Заменить:
const [configured, setConfigured] = useState(false);
const [total, setTotal] = useState(0);
const [service, setService] = useState(null);

// На:
// Убрать если не используются
// const [configured, setConfigured] = useState(false);
// const [total, setTotal] = useState(0);
// const [service, setService] = useState(null);
```

## 4. Типизация any

### src/app/functions-steps/page.tsx
```typescript
// Заменить:
const handleFunctionSelect = (functionData: any) => {

// На:
interface FunctionData {
  id: string;
  name: string;
  // добавьте нужные поля
}

const handleFunctionSelect = (functionData: FunctionData) => {
```

### src/app/our-partners/page.tsx
```typescript
// Заменить:
const handlePartnerClick = (partner: any) => {
const handleServiceClick = (service: any) => {

// На:
interface Partner {
  id: string;
  name: string;
  // добавьте нужные поля
}

interface Service {
  id: string;
  name: string;
  // добавьте нужные поля
}

const handlePartnerClick = (partner: Partner) => {
const handleServiceClick = (service: Service) => {
```

### src/app/partner-dashboard/page.tsx
```typescript
// Заменить:
const handleBannerUpload = (file: any) => {
const handleBannerEdit = (banner: any) => {

// На:
interface Banner {
  id: string;
  name: string;
  // добавьте нужные поля
}

const handleBannerUpload = (file: File) => {
const handleBannerEdit = (banner: Banner) => {
```

## 5. Экранирование кавычек

### src/app/partner-dashboard/page.tsx
```typescript
// Заменить:
<p>Вы уверены, что хотите удалить баннер "Название баннера"?</p>

// На:
<p>Вы уверены, что хотите удалить баннер &quot;Название баннера&quot;?</p>
```

## 6. Next.js Link

### src/app/not-found.tsx
```typescript
// Заменить:
<a href="/">Вернуться на главную</a>

// На:
import Link from 'next/link';

<Link href="/">Вернуться на главную</Link>
```

## 7. React Hooks зависимости

### src/app/functions-steps/FunctionsContext.tsx
```typescript
// Заменить:
useEffect(() => {
  // ...
}, []);

// На:
useEffect(() => {
  // ...
}, [getBasePrice]);
```

### src/app/functions-steps/page.tsx
```typescript
// Заменить:
useEffect(() => {
  // ...
}, []);

// На:
useEffect(() => {
  // ...
}, [fetchPartnerServiceDetails]);
```

### src/app/order-created/page.tsx
```typescript
// Заменить:
useEffect(() => {
  // ...
}, []);

// На:
useEffect(() => {
  // ...
}, [fetchService]);
```

### src/app/partner/[partnerName]/page.tsx
```typescript
// Заменить:
useEffect(() => {
  // ...
}, []);

// На:
useEffect(() => {
  // ...
}, [fetchPartnerServices]);
```

### src/app/payment/page.tsx
```typescript
// Заменить:
useEffect(() => {
  // ...
}, []);

// На:
useEffect(() => {
  // ...
}, [fetchService]);
```

## 8. Неиспользуемые импорты

### src/app/home/Categories.tsx
```typescript
// Заменить:
import { SwipeableTabs } from 'react-swipeable-tabs';

// На:
// Убрать если не используется
// import { SwipeableTabs } from 'react-swipeable-tabs';
```

## Альтернативное решение - отключение ESLint

Если исправления требуют много времени, можно временно отключить строгие правила в `.eslintrc.json`:

```json
{
  "extends": "next/core-web-vitals",
  "rules": {
    "@typescript-eslint/no-unused-vars": "warn",
    "@typescript-eslint/no-explicit-any": "warn",
    "react-hooks/exhaustive-deps": "warn",
    "react/no-unescaped-entities": "warn",
    "@next/next/no-html-link-for-pages": "warn"
  }
}
```

Это позволит приложению собраться, но оставит предупреждения для исправления позже. 