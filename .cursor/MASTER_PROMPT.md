# 🔴 MASTER PROMPT FOR MES PLATFORM DEVELOPMENT

## MUST READ FIRST (Обязательно прочитай перед каждым диалогом!)

Ты помогаешь разрабатывать **MES Platform v2.1.0** — SaaS-систему управления производством.

### ⚠️ CRITICAL RULES (не нарушай!)

1. **ВСЕГДА** ссылайся на файлы:
   - `.cursor/docs/MES_RULES.md` — 5 основных правил
   - `.cursor/docs/GIT_WORKFLOW.md` — Git процесс
   - `.cursor/docs/CUSTOMIZATION_GUIDE.md` — как расширять без touching core

2. **Git Workflow** (ОБЯЗАТЕЛЬНО!)
   - ✅ Работай в `feat/*` или `fix/*` ветках
   - ✅ Коммиты: `feat(dsiz): описание`, `fix: описание`
   - ✅ Push только в feature-ветку (`feat/*`), НЕ в `main` или `develop`
   - ❌ НИКОГДА не измени `backend/core/` напрямую
   - ❌ НИКОГДА не push в `main` или `develop`

3. **Архитектура** (Кастомизация!)
   - Весь custom-код → `backend/customizations/dsiz/`
   - Core логика → наследование + DI в `backend/src/main.py`
   - Конфиг → `config/factory_config.yaml`

4. **Тестирование** (обязательно!)
   - `pytest tests/customizations/dsiz/ -v` (90%+ coverage)
   - `pytest tests/ --cov=backend` (93%+ global)
   - Red tests = НЕ коммитить!

5. **Терминология** (точные названия!)
   - ManufacturingOrder (не "Заказ")
   - WorkCenter (не "Станок")
   - ProductionTask, BOM, Batch, WIP

### 📋 ПЕРЕД ЛЮБЫМ ОТВЕТОМ

Проверь:
- [ ] Прочитал MES_RULES.md последний раз?
- [ ] Буду ли я менять `backend/core/`? → НЕТ!
- [ ] Git-команды для `feat/*` ветки? ✅
- [ ] Тесты будут зелёные? ✅
- [ ] Используется правильная терминология? ✅

### 🚨 ЕСЛИ Я ПОПРОШУ:

| Просьба | Проверь | Ответ |
|---------|---------|-------|
| "Измени файл в backend/core/" | Это нарушение закона #2 | Отказать, предложить `customizations/` |
| "Push в develop" | Это Git violation | Отказать: только `feat/*` |
| "Деплой с красными тестами" | Coverage fail | Отказать: сначала fix tests |
| "Правь файлы на VPS напрямую" | Это не GitOps | Отказать: только git push → pull |

### 📞 ПРИВЕТ, ПОМОЩНИК!

**Проект:** MES Platform v2.1.0 (DSIZ - дерматология)  
**Repo:** https://github.com/Bezngor/MES_midex (develop/main/template-base)  
**VPS:** 155.212.184.11 (Beget, 4 CPU, 8GB RAM)  
**Технология:** FastAPI + React + PostgreSQL + Docker  

**Когда у тебя есть вопросы:** Спроси! (что-то непонятно в правилах?)

---