# .be Domain Checker for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

Een op maat gemaakte Home Assistant custom integratie (volledig geschikt voor HACS) die de status van `.be` domeinnamen controleert door rechtstreeks de officiële WHOIS-server van DNS Belgium te bevragen. Dit gebeurt zonder externe Python-bibliotheken (via sockets), waardoor het razendsnel en uiterst betrouwbaar is op alle Home Assistant-platformen (zoals Raspberry Pi, Home Assistant OS, Docker, etc.).

## Functionaliteiten

- **UI-Configuratie (Config Flow)**: Eenvoudig domeinen toevoegen en het controle-interval instellen via de Home Assistant interface.
- **Sensoren**:
  - `sensor.[domein]_status`: Geeft de directe status weer (`AVAILABLE` of `NOT AVAILABLE`).
  - `binary_sensor.[domein]_available`: Springt op `on` zodra het domein beschikbaar komt, en staat op `off` als het geregistreerd is.
- **Gebeurtenissen (Events)**:
  - Vuurt een event af wanneer een domein beschikbaar komt.
  - Vuurt een event af wanneer de status van een domein verandert.

---

## Installatie

### Optie 1: Via HACS (Aanbevolen)
1. Ga in Home Assistant naar **HACS** -> **Integraties**.
2. Klik rechtsboven op de drie puntjes en kies **Aangepaste repositories** (Custom repositories).
3. Plak de URL van deze GitHub repository bij *Repository* en kies **Integratie** als categorie. Klik op **Toevoegen**.
4. Zoek naar **.be Domain Checker** in HACS en klik op **Downloaden**.
5. Herstart Home Assistant.

### Optie 2: Handmatig
1. Download de code van deze repository.
2. Kopieer de map `custom_components/be_domain_checker` naar de `custom_components/` map in je Home Assistant configuratiemap (bijv. `/config/custom_components/`).
3. Herstart Home Assistant.

---

## Configuratie

1. Ga in Home Assistant naar **Instellingen** -> **Apparaten & Diensten**.
2. Klik rechtsonder op **Integratie toevoegen**.
3. Zoek naar **.be Domain Checker** en selecteer deze.
4. Voer de domeinnaam in (bijv. `xxxx.be` of simpelweg `xxxx` - `.be` wordt automatisch toegevoegd als dit ontbreekt).
5. Voer het gewenste controle-interval in minuten in (standaard 60 minuten).
6. Klik op **Verzenden**. Het domein en de sensoren zijn nu direct aangemaakt en actief!

---

## Gebeurtenissen (Events)

Deze integratie vuurt twee soorten events af op de Home Assistant Event Bus, speciaal bedoeld om direct en efficiënt automatiseringen aan te sturen:

### 1. `be_domain_checker_domain_available`
Dit event wordt afgevuurd zodra een gecontroleerd domein **beschikbaar (`AVAILABLE`)** wordt bevonden.
**Event data:**
```json
{
  "domain": "xxxx.be",
  "status": "AVAILABLE"
}
```

### 2. `be_domain_checker_status_changed`
Dit event wordt afgevuurd bij elke statuswijziging (bijvoorbeeld van `NOT AVAILABLE` naar `AVAILABLE`).
**Event data:**
```json
{
  "domain": "xxxx.be",
  "old_status": "NOT AVAILABLE",
  "new_status": "AVAILABLE"
}
```

---

## Voorbeeld Automatiseringen (Automations)

Je kunt automatiseringen bouwen op basis van de sensoren of direct op basis van de afgevuurde events.

### Voorbeeld 1: Op basis van Event (Aanbevolen voor directe notificaties)
Deze automatisering stuurt een notificatie zodra het domein `xxxx.be` vrijkomt:

```yaml
alias: "🚨 Domein Alert: xxxx.be is VRIJ!"
description: "Stuurt een melding zodra het domein beschikbaar is"
trigger:
  - platform: event
    event_type: be_domain_checker_domain_available
    event_data:
      domain: xxxx.be
action:
  - service: notify.persistent_notification
    data:
      title: "🚨 Domein Alert!"
      message: "Het domein xxxx.be is zojuist vrijgekomen en kan geregistreerd worden!"
```

### Voorbeeld 2: Op basis van de Binary Sensor
Deze automatisering triggert zodra de binary sensor van status verandert naar `on`:

```yaml
alias: "Domein status veranderd naar Vrij"
trigger:
  - platform: state
    entity_id: binary_sensor.xxxx_be_available
    to: "on"
action:
  - service: notify.persistent_notification
    data:
      title: "Domeinnaam Beschikbaar"
      message: "De status van xxxx.be is nu: Vrij!"
```

---

## Licentie

Dit project is gelicentieerd onder de MIT-licentie. Zie het `LICENSE` bestand voor meer informatie.
