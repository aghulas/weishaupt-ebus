# Terms of the comments — English, French, German

## What

Glossary behind the translation files of the configuration fork (`src/fr.yaml`, branch
`weishaupt-L`): one row per term used in the comments of the lots, not per comment string. A
comment is translated by putting the terms of its row(s) together; it counts as `vendor` when
every term has a vendor source, as `provisional` when one of its terms is provisional, as
`owner` otherwise. Names, value lists and units are not translated and have no row.

Status `vendor`: the French term is printed in a French edition of a vendor manual, cited by
document and page. Status `owner`: no manual at hand gives a term; the proposal, in ordinary
heating or computing vocabulary, was read and accepted by the owner of the project, who
operates the test installation (2026-11-18, section "To validate"). Status `provisional`: no
manual gives a term and the proposal has not been read; to be replaced or accepted. A term
found later in a manual or on the display of a device replaces an `owner` or `provisional`
one.

The German column is filled only where a source in this repository gives the term; no record
does yet, so it is empty. It is kept for the German entries of the lots (`docs/i18n.md`,
option B).

## How it was established

Read on 2026-11-17 in the operator's copies of the vendor manuals, French editions, with the
English editions of the same documents where the operator has them to pair a French term with
the English one. No page or passage is copied here: only the term, the document and the page.
The page is the number printed in the footer.

| Ref | Device | Title | Document | Edition | Language |
|---|---|---|---|---|---|
| KA | system manager WCM-KA | Notice de montage et de mise en service, Manager de cascade WCM-KA 3.0 | 83258404 | 1/2013-04, 123 pages | French |
| FS | room unit WCM-FS, heating module WCM-EM | Notice de montage et de mise en service, Commande à distance WCM-FS 2.0 et module d'extension WCM-EM 2.1 | 83277504 | 3/2012-10, 111 pages | French |
| FS-en | the same | Installation and operating instruction, Remote control station WCM-FS 2.0 and extension module WCM-EM 2.1 | 83277502 | 3/2012-10, 106 pages | English |
| FSU-en | room unit WCM-FS, user manual | Operating instruction, Remote control station WCM-FS 2.0 | 83277702 | 1/2012-04, 43 pages | English |
| FB | older room unit WCM-FB, user manual | Notice d'utilisation, Commande à distance WCM-FB | 83053304 | 1/2005, 28 pages | French |
| WTC | boiler WTC-GB | Notice de montage et de mise en service, Chaudière à condensation gaz WTC-GB 120 … 300-A | 83251704 | 1/2020-08, 128 pages | French |
| WTC-en | the same | Installation and operating instruction, Gas condensing boiler WTC-GB 120 … 300-A | 83251702 | 1/2011-02, 106 pages | English |
| SEP | hydraulic separation of a boiler cascade | Notice de montage et de mise en service, Système de séparation hydraulique pour cascade de WTC-GB 120 … 300-A | 83310404 | 1/2020-10, 36 pages | French |

By its number, KA is the French edition of the German manual 83258401 that
`settings-writes.md` cites; there is no English edition of it at hand. The French user manual of the WCM-FS 2.0 (French edition
of 83277702) is not at hand either. Also in the operator's folder and not used: a spare-parts
list of the WTC-GB (2020, three languages; three device names checked in it), the planning
manual of the WTC-GB (document 83527405, title page read only) and a product brochure.

The system-manager settings of lot C were matched to the numbered parameters of KA by range,
unit and factory value: `BlockingTime` = 537 (0 to 30 min, certain), `DHWSwitchDiff` = 575
(-10 to -1 K, certain), `DHWLoadTime` = 577 (10 to 180 min, certain), `LegionellaSetpoint` =
580 (40 to 80 °C; 574 has the same range), `LegionellaCirculationTime` = 583 (3 to 20 min,
certain), `ChangeOverTime` = 532 (factory 50 h as read on the installation; the manual prints
1 to 400 h, the lot 0 to 250), `DeCoupleMinTemp` = 552 by meaning only (the manual prints 8 to
78 °C, the lot 0 to 50), `CalorifierSwitchDiff` not matched (no parameter prints 1 to 20 K).

## Glossary

| English (as the lots write it) | French | German | Source | Status |
|---|---|---|---|---|
| system manager (WCM-KA) | manager de cascade | | KA p. 1, 8; WTC p. 60 | vendor |
| room unit (WCM-FS) | commande à distance | | FS p. 1, 8; WTC p. 42 | vendor |
| heating module (WCM-EM) | module d'extension | | FS p. 1, 8; WTC p. 91 | vendor |
| boiler; WTC | chaudière; chaudière WTC | | KA p. 8, 18; FS p. 7 | vendor |
| first boiler, second boiler | première chaudière, seconde chaudière | | KA p. 18, 93 | vendor |
| cascade | cascade | | KA p. 12, 18 | vendor |
| boiler sequence (of the cascade) | ordre d'enclenchement des chaudières | | KA p. 82 | vendor |
| running time | temps de marche; temps de fonctionnement | | KA p. 81; FS p. 94 | vendor |
| heat source | générateur de chaleur | | FS p. 46 | vendor |
| heating circuit | circuit de chauffage | | FS p. 7, 9; KA p. 10 | vendor |
| heat demand | demande de chaleur | | KA p. 57, 91; WTC p. 16 | vendor |
| temperature | température | | all manuals | vendor |
| temperature difference | différentiel de température | | KA p. 87; WTC p. 14 (also "écart de température", KA p. 97) | vendor |
| setpoint | consigne; consigne de température | | WTC p. 44, 46; KA p. 30 | vendor |
| flow temperature | température de départ | | WTC p. 42; FS p. 28; KA p. 43 | vendor |
| actual (flow temperature) | instantanée | | FS p. 28; WTC p. 55 | vendor |
| flow setpoint | consigne de température départ | | WTC p. 14, 46 (i 13); FS p. 65, 78 | vendor |
| requested (flow setpoint, flow temperature) | demandée | | no vendor term; nearest labels "Temp Cons syst" (FS p. 36), "Demande de chaleur maximale" (WTC p. 46) | owner |
| maximum, minimum flow temperature | température de départ maximale, minimale | | FS p. 57, 58; WTC p. 49; KA p. 57 | vendor |
| limit (maximum flow temperature limit) | limite | | no vendor term; the manuals have no separate term | owner |
| return temperature | température retour | | WTC p. 47 (i 37) | vendor |
| flue gas temperature | température des fumées | | WTC p. 21, 90 (i 31) | vendor |
| boiler temperature | température chaudière | | WTC p. 20; FS p. 59 | vendor |
| outside temperature | température extérieure | | WTC p. 46 (i 33); FS p. 14; KA p. 34 | vendor |
| outside temperature, weighted over time | température extérieure pondérée | | WTC p. 46 (i 12); FS p. 36; KA p. 62 | vendor |
| outside sensor B1 | sonde extérieure B1 | | KA p. 10; FS p. 9; WTC p. 39 | vendor |
| room temperature | température ambiante | | FS p. 28; KA p. 43 | vendor |
| normal (room temperature setpoint) | normale | | KA p. 39 (112); FS p. 32 (P112) | vendor |
| setback (room temperature setpoint) | réduite | | KA p. 40 (113); FS p. 32 (P113) | vendor |
| frost protection | protection hors-gel; hors-gel | | KA p. 45, 58; WTC p. 59 | vendor |
| outside temperature below which the frost protection starts | température limite hors-gel | | FS p. 79 (P502); KA p. 59 (382) | vendor |
| summer / winter changeover | commutation été/hiver | | KA p. 46 (118); FS p. 32 (P119) | vendor |
| steepness of the heating curve | pente de la courbe de chauffe | | FB p. 24; KA p. 43, 44 (116); FS p. 83, 84 | vendor |
| optimised switch-on | optimisation au démarrage | | FS p. 80 (P503); KA p. 60 (383) | vendor |
| lead time (of the optimised switch-on) | durée d'anticipation | | FS p. 80; KA p. 60 | vendor |
| boiler boost offset | surélévation de température chaudière avec circuit mélangé | | FS p. 60 (P424) | vendor |
| operating mode | mode de fonctionnement | | FS p. 28; KA p. 29; WTC p. 43 | vendor |
| operating phase | phase de fonctionnement | | WTC p. 46, 89 (i 10) | vendor |
| status (of a boiler) | état | | WTC p. 42, 88 | vendor |
| status byte | octet d'état | | no vendor term | owner |
| broadcast by | diffusé par | | no vendor term | owner |
| exchange (room unit / heating module) | échange | | no vendor term | owner |
| burner | brûleur | | WTC p. 14 | vendor |
| burner load | puissance du brûleur | | WTC p. 14, 46 (i 11), 58 | vendor |
| current (burner load) | actuelle | | KA p. 109; WTC p. 55 | vendor |
| minimum, maximum burner load | puissance minimale, maximale | | WTC p. 50 (P 36, P 37) | vendor |
| current burner modulation | degré de modulation instantané | | KA p. 109 (603) | vendor |
| ionisation signal | signal d'ionisation | | WTC p. 46, 89 (i 32) | vendor |
| pump (of the boiler) | circulateur | | WTC p. 46, 58 | vendor |
| set speed of the PWM pump | consigne de vitesse du circulateur PWM | | WTC p. 89 (i 22), p. 62 (A32); "pompe PWM" FS p. 63 | vendor |
| burner operating hours | heures de fonctionnement du brûleur | | WTC p. 47 (i 43) | vendor |
| burner starts | démarrages brûleur | | WTC p. 47 (i 42) | vendor |
| operating hours (counter other than the burner hours) | heures de fonctionnement | | no vendor term; the manuals have the burner counter only | owner |
| hours with mains on | heures sous tension | | no vendor term | owner |
| since the last service; maintenance counter | depuis le dernier entretien; compteur d'entretien | | WTC p. 47 (i 46), p. 77 | vendor |
| blocking time (before a further boiler of the cascade is switched on) | temps de blocage | | KA p. 18, 86 (537) | vendor |
| de-couple sensor B22; hydraulic separator | sonde de bouteille casse-pression (B22); bouteille casse-pression | | KA p. 10 to 13, 70, 91; FS p. 9, 66 | vendor |
| plate exchanger, secondary side (sensor B22) | échangeur à plaques, côté secondaire | | KA p. 14 to 16; SEP p. 10, 31 | vendor |
| domestic hot water; hot water | ECS (eau chaude sanitaire) | | FS p. 28, 89; KA p. 30; WTC p. 43 | vendor |
| domestic hot water sensor B3 | sonde ECS B3 | | KA p. 10; FS p. 9; WTC p. 39 | vendor |
| hot water setpoint; configured | consigne de température ECS; réglée | | KA p. 28, 30; WTC p. 44 | vendor |
| hot water operating mode | mode de fonctionnement ECS | | WTC p. 42; KA p. 32 | vendor |
| hot water exceed temperature | surélévation de température ECS | | KA p. 98 (576); FS p. 87 (P603) | vendor |
| switching differential | différentiel de commutation | | KA p. 97 (575); FS p. 86 (P602); WTC p. 51 (P 51) | vendor |
| calorifier | stock tampon | | no sure vendor term: paired through WTC-en p. 25 and WTC p. 30 only; KA p. 93 (562) is the nearest parameter | owner |
| maximum hot water loading time | temps de charge maximal pour l'ECS | | KA p. 99 (577); FS p. 88 (P604) | vendor |
| legionella protection; its setpoint | fonction anti-légionelle; consigne de température anti-légionelle | | KA p. 101, 102 (579, 580); FS p. 89, 91 | vendor |
| circulation pump; circulation | pompe de circulation ECS; circulation ECS | | FS p. 10, 93, 94; KA p. 104 (583) | vendor |
| heating program 1 to 3 | programme de chauffe 1 … 3 | | FS p. 27, 78; KA p. 31, 49; FB p. 11 | vendor |
| hot-water program | programme ECS | | FS p. 32, 97; KA p. 106 | vendor |
| circulation program | programme de circulation ECS | | FS p. 95; KA p. 106 | vendor |
| slot (of a weekly program) | plage horaire | | KA p. 48, 106; FB p. 7, 11 | vendor |
| stored in the room unit | enregistré dans la commande à distance | | no vendor term ("stored"); device name FS p. 1 | owner |
| Monday … Sunday | lundi … dimanche | | KA p. 48, 66, 101; FS p. 39, 89; abbreviations FB p. 13 | vendor |
| day of the week; day of the month; month; year | jour de la semaine; jour du mois; mois; année | | KA p. 48; FB p. 15 | vendor |
| hour, minute, second; hours, minutes, seconds | heure, minute, seconde; heures, minutes, secondes | | FB p. 15; KA p. 27, 105, 110 | vendor |
| percent | pour cent | | no vendor term; the manuals print the sign only | owner |
| fault | défaut | | WTC p. 86; KA p. 31; FS p. 53 | vendor |
| warning | alarme | | WTC p. 86, 87, 90; FB p. 23 | vendor |
| fault counters (of the boiler automat) | compteurs de défauts | | no vendor term; the manuals list the codes, not the counters | owner |
| first answer byte (of a memory read); number of bytes asked for | premier octet de la réponse; nombre d'octets demandés | | no vendor term; not a manual notion | owner |
| safety temperature limiter (eSTL) | thermostat de sécurité (limiteur) | | WTC p. 89 (i 30), 90, 92 | vendor |
| flow sensor; return sensor; flue gas sensor; defective | sonde de départ; sonde de retour; sonde de fumées; défectueuse | | WTC p. 90, 92 | vendor |
| no flame at burner start; flame lost during operation; flame signal without a flame | pas de formation de flamme au démarrage du brûleur; perte de flamme en fonctionnement; flamme parasite | | WTC p. 90, 92 | vendor |
| air pressure switch; flue gas pressure switch; rest position | pressostat d'air; pressostat fumées; position de repos | | WTC p. 76, 92, 93 | vendor |
| fan; fan speed not reached; fan standstill check | ventilateur; vitesse du ventilateur non atteinte; contrôle à l'arrêt du ventilateur | | WTC p. 92, 93 | vendor |
| gas valve leaking; gas pressure too low | multibloc gaz non étanche; pression gaz trop faible | | WTC p. 90, 92 | vendor |
| water pressure too low | pression installation trop faible | | WTC p. 92 | vendor |
| flue gas damper, run time exceeded | clapet de fumées, durée d'enclenchement maximale dépassée | | WTC p. 90, 93 | vendor |
| input H2; lockout input; condensate lifting unit | entrée H2; verrouillage brûleur; dispositif de relevage des condensats | | WTC p. 90, 93 | vendor |
| data record error (boiler, burner); supply out of tolerance; reset too often | erreur de transmission des données (chaudière, brûleur); alimentation électrique hors tolérances; déverrouillée trop fréquemment | | WTC p. 93 | vendor |
| automat; operating unit (of the boiler) | électronique chaudière (WCM-CPU); tableau de commande chaudière (WCM-CUI) | | WTC p. 91, 93 | vendor |
| fault history (boiler) | mémoire de défauts | | WTC p. 45, 88 | vendor |
| fault log (system manager) | historique des défauts | | KA p. 110 (608); FS p. 53 (P338) | vendor |
| fault code | code défaut | | KA p. 110; FS p. 53; WTC p. 88 | vendor |
| device that raised (a fault) | origine | | KA p. 109, 110; FS p. 53 | vendor |
| slot (of the fault history) | emplacement | | no vendor term; the display numbers the faults 1 to 6 by age (WTC p. 88), a slot is a place in memory | owner |
| selected entry (of the fault log) | entrée sélectionnée | | no vendor term; the manual says "indication de défaut 01" (KA p. 110) | owner |
| fault number | numéro de défaut | | no vendor term | owner |
| fault type | type de défaut | | no vendor term | owner |
| address of the last byte written | adresse du dernier octet écrit | | no vendor term | owner |
| error status | code défaut | | no vendor term for the value; "code défaut", and code 00 for a cleared fault, KA p. 110 | owner |
| firmware version | version du logiciel | | KA p. 109 (609); FS p. 52; WTC p. 47 (i 44) | vendor |
| major part, minor part (of the version) | partie majeure, partie mineure | | no vendor term | owner |
| configuration | configuration | | KA p. 65; FS p. 36; WTC p. 48 | vendor |
| configuration status | état de la configuration | | no vendor term ("status") | owner |

The 24 comments of the Wolf messages that share `wolf/broadcast` with the lots (room controller
target values and operational data, control commands, network messages) come from the official
configuration, not from the lots. They have no row here and no vendor source, and since
2026-11-18 no entry in `src/fr.yaml`: on the owner's decision they stay in English.

## Coverage of `src/fr.yaml`

At `weishaupt-L` `d5a88bd` (local, 2026-11-18): 293 comment strings in the files of the lots
and `wolf/broadcast`, 269 of them of the lots (`scripts/i18n-keys.py`), all 269 with a key.

| Kind | Strings | Vendor terms only | Accepted by the owner | Provisional | Left in English |
|---|---|---|---|---|---|
| Written by hand, lots | 137 | 109 | 28 | 0 | |
| Patterned (program slots, fault-history slots) | 132 | 84 | 48 | | |
| Wolf messages of the broadcast file | 24 | | | | 24 |
| All | 293 | 193 | 76 | 0 | 24 |

The 48 patterned strings accepted by the owner are the 42 "stored in the room unit" slots and
the 6 fault-history slots. The 8 fault-counter strings of lot J (seven message comments —
"fault counters, numbers 57 to 51" … — and the comment of the first answer byte), written
after the list below was first made, were put to the owner on 2026-11-18 and accepted as
written, so their two terms are now `owner` and no lot has a provisional string left. The
Wolf messages are left in English on the
owner's decision of 2026-11-18; the key check does not expect a key for them.

## To validate

Proposals written where the sources did not settle a term or a choice. Each is in `src/fr.yaml`
or in the scripts as proposed; tick a line when the owner has accepted it, or replace the
proposal. "Why" says what the manuals lack.

The owner went through the list on 2026-11-18. A ticked line is accepted as written, or as
changed where the line says so; an unticked line was not put to the owner.

### Comments written by hand

| | English string | French proposal | Why the sources did not settle it | Alternative |
|---|---|---|---|---|
| [x] | requested flow setpoint | consigne de température départ demandée | no manual has a word for "requested"; nearest label "Temp Cons syst" (FS p. 36) | consigne de température du système |
| [x] | flow temperature the heating circuit requests from the heat source | température de départ demandée par le circuit de chauffage au générateur de chaleur | same; the boiler manual calls its side "Demande de chaleur maximale" (WTC p. 46) | demande de chaleur du circuit de chauffage (température de départ) |
| [x] | maximum flow temperature limit | limite de la température de départ maximale | the manuals have "température de départ maximale" only, no separate limit | température de départ maximale |
| [x] | room-controller / heating-module exchange | échange entre commande à distance et module d'extension | device names are the vendor's, the message itself is not described | dialogue commande à distance / module d'extension |
| [x] | switching differential of the calorifier | différentiel de commutation du stock tampon | "calorifier" is paired with "stock tampon" in one place only (WTC-en p. 25, WTC p. 30); no parameter has the range of the register | différentiel de commutation du préparateur ECS |
| [x] | status byte | octet d'état | not a manual notion | octet de statut |
| [x] | boiler status broadcast by the WTC | état de la chaudière diffusé par la WTC | not a manual notion | état de la chaudière émis par la WTC |
| [x] | configuration status | état de la configuration | the manuals have "configuration" and "Config …" labels, no status | configuration |
| [x] | error status, 0 when no error is pending | code défaut, 0 en l'absence de défaut (changed by the owner; the proposal was "état de défaut, 0 en l'absence de défaut") | no such value in the manuals; code 00 is a cleared fault there (KA p. 110) | none left |
| [x] | firmware version, major part / minor part | version du logiciel, partie majeure / partie mineure | "version du logiciel" is the vendor's; the split is not in the manuals | version du logiciel, numéro majeur / numéro mineur |
| [x] | hours with mains on | heures sous tension | the manuals have the burner counter only | heures de mise sous tension |
| [x] | operating hours, burner hours and burner starts | heures de fonctionnement, heures brûleur et démarrages brûleur | no counter of operating hours apart from the burner's (WTC p. 47) | heures sous tension, heures brûleur et démarrages brûleur |
| [x] | fault number | numéro de défaut | the manual says "Code défaut" and "Code d'alarme"; the field serves both | numéro du code (défaut ou alarme) |
| [x] | fault history: address of the last byte written | mémoire de défauts : adresse du dernier octet écrit | internal of the automat, not in the manuals | mémoire de défauts : pointeur d'écriture |
| [x] | selected fault-log entry (0 = most recent) | entrée sélectionnée de l'historique des défauts (0 = la plus récente) | the manual says "indication de défaut 01" for an entry (KA p. 110) | indication de défaut sélectionnée (0 = la plus récente) |
| [x] | fault code of the selected entry | code défaut de l'entrée sélectionnée | follows the line above | code défaut de l'indication sélectionnée |
| [x] | fault type of the selected entry | type de défaut de l'entrée sélectionnée | no "type" of a fault in the manuals | nature du défaut de l'entrée sélectionnée |
| [x] | device that raised the selected entry | origine du défaut de l'entrée sélectionnée | "origine" is the vendor's (KA p. 109); "entry" is not | appareil à l'origine de l'entrée sélectionnée |
| [x] | percent | pour cent | the manuals print the sign only | pourcentage |
| [x] | fault counters, numbers `<a>` to `<b>` (the seven lot-J reads) | compteurs de défauts, numéros `<a>` à `<b>` | no vendor term; the manuals list the fault codes, not counters of them | compteurs par code défaut |
| [x] | first answer byte: 0, or the number of bytes asked for when all counters read 0 | premier octet de la réponse : 0, ou le nombre d'octets demandés quand tous les compteurs sont lus à 0 | not a manual notion | none |

The two lines above were added after the owner's first pass, once lot J existed, and put to
the owner on 2026-11-18 as well; both accepted as written.

### Patterned comments

| | English pattern | French proposal | Why | Alternative |
|---|---|---|---|---|
| [x] | hot-water program stored in the room unit, `<day>` slot `<n>` (21) | programme ECS enregistré dans la commande à distance, `<jour>`, plage horaire `<n>` | "stored" has no vendor wording | programme ECS mémorisé dans la commande à distance, … |
| [x] | circulation program stored in the room unit, `<day>` slot `<n>` (21) | programme de circulation ECS enregistré dans la commande à distance, `<jour>`, plage horaire `<n>` | same | programme de bouclage ECS … (the boiler manual says "bouclage", WTC p. 60) |
| [x] | fault history slot `<n>` (6) | mémoire de défauts, emplacement `<n>` | the display numbers the faults by age (WTC p. 88); a slot is a place in memory | mémoire de défauts, défaut `<n>` |
| [x] | slot of a weekly program, all 126 program strings | plage horaire | vendor term of the system manager (KA p. 48, 106) and of the older room unit; the French screens of the WCM-FS 2.0 are not at hand | cycle (FB p. 13, 16); période |

### Wolf messages of the broadcast file (24 strings, no vendor source)

| | English strings | Decision |
|---|---|---|
| [x] | the 24 comments of the Wolf messages of `wolf/broadcast` (room controller target values and operational data, control commands, network messages) | left in English (owner, 2026-11-18): the proposals were removed from `src/fr.yaml` (`a22b797`) |

### Choices of wording where the vendor's French varies

| | Choice made | Other form in the manuals |
|---|---|---|
| [x] | "ECS" everywhere, never spelled out | "eau chaude sanitaire" (FS p. 89, once) |
| [x] | "hors-gel" | "antigel" (labels of FS and KA) |
| [x] | "programme de chauffe" | "programme de chauffage" (FS p. 83) |
| [x] | "bouteille casse-pression" | "bouteille de découplage" (WTC p. 58) |
| [ ] | "anti-légionelle" | "anti-légionnelle" (FS) |
| [x] | "circulateur" for the boiler pump, "pompe de circulation ECS" for the circulation | "pompe" (FS), "circulateur de bouclage ECS" (WTC p. 48) |
| [x] | "puissance du brûleur" for burner load | "modulation", "degré de modulation" (KA) |
| [x] | "différentiel de température" (changed by the owner; the choice was "écart de température") | "écart de température" (KA p. 97) |
| [x] | `BlockingTime`: comment of lot A corrected on 2026-11-17, French "temps de blocage avant enclenchement d'une chaudière supplémentaire de la cascade" | was "temps de blocage minimal du brûleur" |
| [x] | `BurnerServiceHours`: comment of lot E corrected to "i46" on 2026-11-17, French follows | was "i45" |

### Design choices the brief left open

| | Choice | Why | Alternative |
|---|---|---|---|
| [ ] | `weishaupt-L` is the top of `STACK` | one file no lot touches: the stack stays linear and the integration branch holds what the release compiles | apply it after the stack, outside `STACK` |
| [ ] | no `compile-fr` script in `package.json` | the check and the release pass the file to the emitter; `weishaupt-L` stays one file | add it as the prototype did |
| [x] | the 24 Wolf strings of `wolf/broadcast` stay in English (changed by the owner; they had been translated) | they are upstream's comments on Wolf devices, without a vendor source | translate them so that the file is in one language |
| [ ] | the key check counts, in `wolf/broadcast.csv`, the messages of the lots only (`LOT_BROADCAST`, default `KaStatus`); changed with the line above | the Wolf messages need no key any more | count the whole file and report 24 strings without a key |
| [ ] | a key that matches nothing fails only for a file the base ref does not have | `fr.yaml` is the fork's; upstream's `de.yaml` has 820 such keys | a list of strict files |
| [ ] | the check compiles a German tree too | `de.yaml` has 6 keys of the lot strings, the rule is "a file with keys of the lot files" | compile only the fork's own files (shorter check) |
| [ ] | languages of the release: `RELEASE_LANGS`, default `fr`; no German archive | six coincidental German words are not a translation | one archive per compiled language |
| [ ] | trial archives named `0.3.0-dev` | not to be taken for a release | none kept |
| [ ] | value lists (operating phases, on / off) are left in English | they are what `write` and MQTT use; the emitter cannot translate them | a later mechanism; the French names are in WTC p. 46 |

## Findings: English wording of the lots and of the vendor

Where the lots word a thing differently from the vendor's English manuals. Nothing was changed
in the lots; the French follows the vendor's French in each case.

| The lots write | The vendor's English manual writes | Where |
|---|---|---|
| flow (temperature, setpoint) | "supply" in FS-en throughout; WTC-en uses "flow" and "supply" for the same value | FS-en p. 26, 35, 53; WTC-en p. 35, 39 |
| outside (temperature, sensor) | "external" | FS-en p. 13, 23; WTC-en p. 39 |
| weighted over time | "average external temperature"; "dampened" | WTC-en p. 39 (i 12); FS-en p. 34 |
| steepness of the heating curve | "Gradient"; the curve is the "heating reference line" | FS-en p. 30, 79; FSU-en p. 31 |
| hot water, domestic hot water | "DHW" | FS-en, WTC-en throughout |
| operating mode | "Type of operation" | FS-en p. 26; WTC-en p. 39 (i 20) |
| burner load | "Rating" for the value i 11; "load" for the limits P 36 to P 38 | WTC-en p. 39, 42 |
| set speed of the PWM pump | "Setpoint speed pump" (also "Pump rating" for the same i 22) | WTC-en p. 39, 74 |
| hot water exceed temperature | "DHW boost"; "Temperature increase during DHW operation" | FS-en p. 83 (P603); WTC-en p. 43 (P 50) |
| boiler boost offset | "Boil-MC-boost", boiler mixer circuit boost | FS-en p. 56 (P424) |
| lead time of the optimised switch-on | "switch on optimisation", "pre-set time" | FS-en p. 76 (P503) |
| switching differential | "switch diff", "switch differential"; "Switching differential DHW" in the boiler manual | FS-en p. 82; WTC-en p. 43 |
| fault (log, code) on the system manager | "Error history", "Error code", "error source" | FS-en p. 49 |
| fault, warning on the boiler | "Faults" (F), "Warnings" (W), "Fault history": same as the lots | WTC-en p. 73, 74 |
| firmware version | "Software version" | FS-en p. 48; WTC-en p. 40 |
| hydraulic separator | "de-couple", "hydraulic de-couple" | FS-en p. 62; WTC-en p. 48 |
| room unit, heating module, system manager | "remote control station", "extension module", "cascade manager" | FS-en p. 7; FSU-en p. 11 |
| summer / winter changeover | "Summer/Winter change-over" | FSU-en p. 33 |

Findings on content, for the owner:

- **`BlockingTime`** (`15.w.ka`, "minimum burner blocking time") is parameter 537 of the
  system manager by range (0 to 30 min). KA p. 86 describes 537 as the time during which a
  further boiler of the cascade is not switched on, not as a blocking time of the burner; the
  burner's own anti-cycling time is parameter P 34 of the boiler (WTC p. 49, 1 to 15 min).
  **Corrected on 2026-11-17 on the owner's word**: the comment now reads "blocking time
  before a further boiler of the cascade is switched on" (lot A, `66b775e`). From the manual,
  not from a test.
- **`BurnerServiceHours`** ("maintenance counter i45"): in both editions of the boiler manual
  the time since the last service is info value i 46, in tens of hours, and i 45 is the
  software version of the control panel (WTC p. 47, WTC-en p. 40). Neither says the counter
  counts burner hours. The comment may carry a wrong code; the manuals are of 2011 and 2020,
  the automat software on the installation may number differently, but the vendor service
  tool on it shows I45 as the version of the control panel and I46 as the burner operation
  since the last service (`service-tool-log.md`). **Corrected on 2026-11-17 on the owner's
  word**: the comment says i46 (lot E, `3e9347f`).
- **`CalorifierSwitchDiff`**: no parameter of KA prints 1 to 20 K. "Calorifier" appears in
  the vendor's English only as an info value (FSU-en p. 11) and once in WTC-en (p. 25), where
  the French edition says "stock tampon". The French uses that word, provisionally; if the
  register is the differential of the hot-water tank, the French term is "préparateur ECS"
  (FS p. 9).
- **`ChangeOverTime`** and **`DeCoupleMinTemp`**: the ranges of the lot (0 to 250 h, 0 to
  50 °C) are not those the manual prints for 532 (1 to 400 h) and 552 (8 to 78 °C).
- **Sensor B22**: KA names B22 as the lot does (separator, or exchanger secondary side), with
  one page (p. 62) that swaps B22 and B24. The boiler and room-unit manuals know the
  separator sensor as B11, on the boiler.
- **Fault log entry**: the display numbers the entries from 01, the most recent (KA p. 110);
  the lot's `ErrorId` counts from 0. Not a contradiction, the register is an index.
- **Operating phases**: the value-list entries of the lots are the vendor's English phase
  names (WTC-en p. 39); `ForcedVenting` (9) is in neither edition. Value lists are not
  translated; the French names are in WTC p. 46 if a later mechanism needs them.

## Not verified

- No term was checked on the display of a device. The French display of the WCM-FS 2.0 time
  programs (weekday list, name of a switching period) is in a manual not at hand; "plage
  horaire" is the wording of the system-manager manual and of the older room unit.
- The manuals were read as text extracted from the PDF files; a term printed only inside a
  picture of a display may have been missed, and page numbers were not checked against paper.
- The pairing of a comment with a vendor term rests on the meaning of the comment, and for
  eight settings on the ranges above; it was not checked by changing a setting.
- The French manuals vary: "hors-gel" and "antigel", "programme de chauffe" and "programme de
  chauffage", "bouteille casse-pression" (KA, FS) and "bouteille de découplage" (WTC),
  "légionelle" and "légionnelle". One form was chosen per term.

## Equipment and date

Manuals of the device types of the test installation: two WTC-GB condensing boilers in
cascade, system manager WCM-KA, room units WCM-FS and heating modules WCM-EM. 2026-11-17.
