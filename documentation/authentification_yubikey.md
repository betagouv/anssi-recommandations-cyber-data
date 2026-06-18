# Enrôlement de la yubikey

**Pré-requis :**
- Une yubikey
- Un navigateur compatible avec WebAuthn
- la dépendance `webauthn`

## Enregistrement
### Enrôlement depuis le navigateur
- Se rendre sur le site `https://app-45a09cd5-dc7e-420b-96c1-f59129b448c4.cleverapps.io/`
- Avoir sa yubikey branchée
- Saisir "prénom.nom" puis cliquez sur "Enrôlement"
- Cliquez dans la popup qui s'ouvre sur la clé
- Saisissez votre code pin


### Demander à l'admin
Une fois l'étape ci-dessus faite, contactez votre administrateur pour qu'il puisse récupérer votre clé publique et l'ajouter dans la variable d'environnement afin que vous puissiez vous authentifier.

## Connection
Une fois enrôlé, vous pouvez vous connecter via la page `https://app-45a09cd5-dc7e-420b-96c1-f59129b448c4.cleverapps.io/` en remplissant "prénom.nom" puis login avec votre clé branchée.

### Fonctionnement

## Processus complet

# Authentification avec Yubikey

## Enrôlement et connexion

```mermaid
sequenceDiagram
    autonumber

    actor U as Utilisateur
    participant N as Navigateur
    participant S as Service d'authentification
    participant Y as YubiKey
    actor A as Administrateur
    participant C as Utilisateurs autorisés

    rect rgb(255, 255, 255)
        Note over U,C: 1. Enrôlement de la YubiKey

        U->>N: Saisit son identifiant prénom.nom
        U->>N: Clique sur Enrôlement

        N->>S: Demande la création d'un credential

        S->>S: Génère un challenge aléatoire
        S->>S: Associe la demande au domaine de l'application
        S->>S: Exige une vérification par PIN et présence physique

        S-->>N: Demande d'enrôlement WebAuthn

        N->>Y: Demande la création d'un credential
        Y->>U: Demande le code PIN
        U->>Y: Saisit le code PIN
        Y->>U: Demande de toucher la clé
        U->>Y: Touche la YubiKey

        Y->>Y: Génère une paire de clés cryptographiques
        Note right of Y: La clé privée reste<br/>dans la YubiKey

        Y-->>N: Retourne le credential WebAuthn

        N->>S: Transmet la preuve d'enrôlement

        S->>S: Vérifie le challenge
        S->>S: Vérifie le domaine d'origine
        S->>S: Vérifie le RP ID
        S->>S: Extrait le credential ID et la clé publique

        S-->>U: Enrôlement terminé

        U->>A: Demande l'activation de son accès
        A->>C: Associe prénom.nom au credential ID<br/>et à la clé publique
        C-->>A: Utilisateur autorisé
    end

    rect rgb(235, 255, 235)
        Note over U,C: 2. Connexion au tableau de bord

        U->>N: Saisit son identifiant prénom.nom
        U->>N: Clique sur Login

        N->>S: Demande une authentification

        S->>C: Recherche l'utilisateur
        C-->>S: Renvoie l'utilisateur

        S->>S: Génère un nouveau challenge aléatoire
        S->>S: Stock le challenge dans la session serveur
        S-->>N: Demande d'authentification WebAuthn

        N->>Y: Demande une preuve de possession de la clé
        Y->>U: Demande le code PIN
        U->>Y: Saisit le code PIN
        Y->>U: Demande de toucher la clé
        U->>Y: Touche la YubiKey

        Y->>Y: Produit une preuve cryptographique<br/>liée au challenge et au domaine
        Note right of Y: La clé privée ne quitte<br/>jamais la YubiKey

        Y-->>N: Retourne la preuve WebAuthn
        N->>S: Transmet la preuve d'authentification

        S->>C: Retrouve la clé publique<br/>grâce au credential ID
        C-->>S: Clé publique autorisée

        S->>S: Vérifie la signature cryptographique
        S->>S: Vérifie le challenge
        S->>S: Vérifie le domaine d'origine
        S->>S: Vérifie le RP ID

        alt Preuve valide
            S->>S: Crée une session valable 2 heures
            S-->>N: Enregistre le cookie de session
            N-->>U: Affiche le tableau de bord
        else Preuve invalide
            S-->>N: Refuse l'authentification
            N-->>U: Affiche un accès refusé
        end
    end
```





















