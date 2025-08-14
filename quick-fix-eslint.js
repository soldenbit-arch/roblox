#!/usr/bin/env node

/**
 * Быстрый скрипт для исправления основных ESLint ошибок
 * Запуск: node quick-fix-eslint.js
 */

const fs = require('fs');
const path = require('path');

// Функция для замены текста в файле
function replaceInFile(filePath, searchValue, replaceValue) {
    try {
        let content = fs.readFileSync(filePath, 'utf8');
        const originalContent = content;
        
        content = content.replace(searchValue, replaceValue);
        
        if (content !== originalContent) {
            fs.writeFileSync(filePath, content, 'utf8');
            console.log(`✅ Исправлен файл: ${filePath}`);
            return true;
        }
        return false;
    } catch (error) {
        console.error(`❌ Ошибка при обработке ${filePath}:`, error.message);
        return false;
    }
}

// Функция для исправления catch блоков
function fixCatchBlocks(filePath) {
    const catchPattern = /} catch \(error\) \{[\s\S]*?console\.error\('Error:', error\);[\s\S]*?return NextResponse\.json\(\{ error: 'Internal Server Error' \}, \{ status: 500 \}\);[\s\S]*?\}/g;
    
    return replaceInFile(filePath, catchPattern, (match) => {
        // Заменяем error на _error чтобы избежать неиспользуемой переменной
        return match.replace(/error/g, '_error');
    });
}

// Функция для исправления неиспользуемых переменных состояния
function fixUnusedState(filePath) {
    const patterns = [
        // Неиспользуемые useState
        /const \[selectedPartnerFunctions, setSelectedPartnerFunctions\] = useState\(\[\]\);/g,
        /const \[banners, setBanners\] = useState\(\[\]\);/g,
        /const \[bannersLoading, setBannersLoading\] = useState\(false\);/g,
        /const \[editingBanner, setEditingBanner\] = useState\(null\);/g,
        /const \[configured, setConfigured\] = useState\(false\);/g,
        /const \[total, setTotal\] = useState\(0\);/g,
        /const \[service, setService\] = useState\(null\);/g,
        
        // Неиспользуемые параметры
        /const \{ username, email, password \} = req\.body;/g,
        /const \{ username, email \} = req\.body;/g,
        
        // Неиспользуемые переменные в колбэках
        /\(err, docs\) => \{/g,
        /\(err, result\) => \{/g,
        /\(err, data\) => \{/g,
    ];
    
    let fixed = false;
    patterns.forEach(pattern => {
        if (replaceInFile(filePath, pattern, (match) => {
            // Комментируем неиспользуемые переменные
            return `// ${match}`;
        })) {
            fixed = true;
        }
    });
    
    return fixed;
}

// Функция для исправления типизации any
function fixAnyTypes(filePath) {
    const patterns = [
        /: any\)/g,
        /: any,/g,
        /: any\s*\{/g,
    ];
    
    let fixed = false;
    patterns.forEach(pattern => {
        if (replaceInFile(filePath, pattern, (match) => {
            // Заменяем any на unknown (более безопасно)
            return match.replace(/any/g, 'unknown');
        })) {
            fixed = true;
        }
    });
    
    return fixed;
}

// Функция для исправления кавычек
function fixQuotes(filePath) {
    const patterns = [
        /"([^"]*)"([^"]*)"([^"]*)"/g,
    ];
    
    let fixed = false;
    patterns.forEach(pattern => {
        if (replaceInFile(filePath, pattern, (match, before, middle, after) => {
            // Экранируем внутренние кавычки
            return `"${before}&quot;${middle}&quot;${after}"`;
        })) {
            fixed = true;
        }
    });
    
    return fixed;
}

// Функция для исправления HTML ссылок
function fixHtmlLinks(filePath) {
    const patterns = [
        /<a href="\/">([^<]*)<\/a>/g,
    ];
    
    let fixed = false;
    patterns.forEach(pattern => {
        if (replaceInFile(filePath, pattern, (match, text) => {
            // Заменяем на Next.js Link
            return `<Link href="/">${text}</Link>`;
        })) {
            fixed = true;
        }
    });
    
    return fixed;
}

// Основная функция исправления
function fixESLintErrors() {
    console.log('🔧 Начинаю исправление ESLint ошибок...\n');
    
    const filesToFix = [
        'src/app/api/partner-orders/route.ts',
        'src/app/api/partner-orders-all/route.ts',
        'src/app/api/partner-services/route.ts',
        'src/app/api/partners/route.ts',
        'src/app/api/user-orders/route.ts',
        'src/app/functions-steps/page.tsx',
        'src/app/home/Categories.tsx',
        'src/app/not-found.tsx',
        'src/app/order-created/page.tsx',
        'src/app/our-partners/page.tsx',
        'src/app/partner/[partnerName]/page.tsx',
        'src/app/partner-dashboard/page.tsx',
        'src/app/payment/page.tsx',
    ];
    
    let totalFixed = 0;
    
    filesToFix.forEach(filePath => {
        if (fs.existsSync(filePath)) {
            console.log(`📁 Обрабатываю: ${filePath}`);
            
            let fileFixed = false;
            
            // Исправляем различные типы ошибок
            if (fixCatchBlocks(filePath)) fileFixed = true;
            if (fixUnusedState(filePath)) fileFixed = true;
            if (fixAnyTypes(filePath)) fileFixed = true;
            if (fixQuotes(filePath)) fileFixed = true;
            if (fixHtmlLinks(filePath)) fileFixed = true;
            
            if (fileFixed) {
                totalFixed++;
            } else {
                console.log(`   ⚠️  Файл не требует исправлений`);
            }
        } else {
            console.log(`❌ Файл не найден: ${filePath}`);
        }
        console.log('');
    });
    
    console.log(`🎉 Исправление завершено!`);
    console.log(`📊 Всего исправлено файлов: ${totalFixed}`);
    
    if (totalFixed > 0) {
        console.log('\n💡 Теперь попробуйте собрать проект снова:');
        console.log('   npm run build');
    }
}

// Запуск скрипта
if (require.main === module) {
    fixESLintErrors();
}

module.exports = { fixESLintErrors }; 