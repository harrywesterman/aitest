# Testplan: com.miui.calculator

## Overzicht

De Android Calculator app (com.miui.calculator — Xiaomi/MIUI variant) is een standaard systeem-app. Dit plan beschrijft de screens, assertions en acties voor geautomatiseerde exploratie en testgeneratie.

## Screens & Scenario's

### 1. Basis Calculator Scherm

**Beschrijving:** Eerste scherm met cijferknoppen (0-9), basisoperators (+, -, ×, ÷), =, C/CE, decimale punt, en result display.

**Assertions (stabiele elementen):**
- Knoppen voor cijfers 0 t/m 9 zijn zichtbaar
- Knoppen voor +, -, ×, ÷ zijn zichtbaar
- = knop is zichtbaar
- C (clear) knop is zichtbaar
- Decimale punt (,) knop is zichtbaar
- Result display/formula bar is zichtbaar

**Actie:** Tik op cijfer `1`, dan `+`, dan `2`, dan `=` — controleer dat resultaat `3` toont.

**Te vermijden (dynamische waarden):**
- Het exacte resultaat in de display (behalve bij eenvoudige som)

### 2. Geavanceerd Paneel (Scientific Mode)

**Beschrijving:** Bij landscape of via swipe naar links/rechts worden wetenschappelijke functies getoond (sin, cos, tan, log, sqrt, etc.).

**Assertions:**
- sin, cos, tan knoppen zijn zichtbaar
- log, ln knoppen zijn zichtbaar
- √ (square root) knop is zichtbaar
- π (pi) knop is zichtbaar
- ( ) haakjes knoppen zijn zichtbaar

**Actie:** Tik op een wetenschappelijke functie (bv. sin) en controleer dat de display reageert.

### 3. History / Rekenlog (indien beschikbaar)

**Beschrijving:** Een schuifbaar paneel met eerdere berekeningen.

**Assertions:**
- Geschiedenis-paneel toont eerdere berekeningen
- Wis geschiedenis knop is zichtbaar

**Actie:** Tik op geschiedenis-knop, controleer dat lijst zichtbaar is, wis geschiedenis.

---

## Test Scenario's

### Scenario A: Basis optelling
1. Tik `5`
2. Tik `+`
3. Tik `3`
4. Tik `=`
5. Assert: display toont `8`

### Scenario B: Delen door nul
1. Tik `1`
2. Tik `÷`
3. Tik `0`
4. Tik `=`
5. Assert: error message of `∞` wordt getoond

### Scenario C: Decimaal getal
1. Tik `7`
2. Tik `,`
3. Tik `5`
4. Tik `×`
5. Tik `2`
6. Tik `=`
7. Assert: display toont `15`

### Scenario D: Clear functie
1. Tik `1` `2` `3`
2. Tik C (clear)
3. Assert: display is leeg of toont `0`

### Scenario E: Procent berekening
1. Tik `2` `0` `0`
2. Tik `%`
3. Assert: display toont `2` (of 1% van 200)

---

## Uit te voeren stappen

1. Start Calculator app via ADB / Appium
2. Basic scherm: capture XML, stuur naar LLM voor element-analyse
3. Voer basis som uit, capture vervolgscherm
4. Swipe of rotatie naar scientific mode, capture XML
5. Als history paneel bestaat, open het en capture
6. Genereer pytest bestand met assertions voor elk scherm

## Notities

- Gebruik `AppiumBy.ANDROID_UIAUTOMATOR` met `UiSelector().text()` voor text-gebaseerde elementen
- Gebruik `AppiumBy.ID` voor resource-id waar beschikbaar
- Sla screenshots op voor visuele verificatie
- Max 10 screens per explore-sessie
