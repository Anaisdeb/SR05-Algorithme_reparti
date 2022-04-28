# SR05 - Projet de Programmation

## Table des matières
1. [Présentation](#Présentation)
2. [Installation et Lancement du projet](#InstallationPresentation) <br/>
    a. [Installation](#Installation) <br/>
    b. [Lancement](#Lancement)
4. [Principe de fonctionnement](#Principe_de_fonctionnement) <br/>
    a. [Activité 4](#Activité_4) <br/>
    b. [Algorithme de file d'attente](#Algorithme_de_file_d'attente) <br/>
    c. [Algorithme de sauvegarde](#Algorithme_de_sauvegarde) <br/>
    d. [Algorithme de l'application de base](#Algorithme_de_l'application_de_base) <br/>
5. [Scénarios de fonctionnement](#Scenario)
6. [Documentation](#Documentation)

## Présentation  <a class="anchor" id="Présentation"></a>

Ce projet a été réalisé dans le cadre de l'enseignement SR05 en Printemps 2022. Celui-ci concerne l'implémentation d'un algorithme réparti qui:
- Dans un premier temps, combine l'algorithme de sauvegarde et de file d'attente. Cela permet de capturer le réseau à certains moments, et de régir les demandes d'entrées en section entre les différents sites. 
- Dans un second temps, permet l'accès à un fichier en lecture/écriture lors d'une section critique.

## Installation et Lancement du projet  <a class="anchor" id="InstallationPresentation"></a>

### Installation <a class="anchor" id="Installation"></a>

Dans un premier temps, il est nécessaire de cloner le projet sur Gitlab :`

Si le compte possède une clé SSH : 
```
git clone git@gitlab.utc.fr:rdelaage/sr05-projet.gi`
```
Sinon :
```
git clone https://gitlab.utc.fr/rdelaage/sr05-projet.git
```

### Lancement <a class="anchor" id="Lancement"></a>

Pour lancer le projet, il est nécessaire de créer dans un premier temps un pipe nommé dans /tmp (par exemple)  avec la commande suivante : 
```
mkfifo /tmp/f
```
Ensuite, dans le dossier du projet, il faut lancer le programme net.py 3 fois sur la même ligne de commande pour avoir accès à l'interface d'utilisation du projet. Il est à noter qu'il faut nommer chaque site avec un numéro en paramètre, à partir de 0 et consécutifs. On aurait avec 3 sites par exemple :
```
./net.py 0 < /tmp/f | ./net.py 1 | ./net.py 2 > /tmp/f

ou 

python3 ./net.py 0 < /tmp/f |python3 ./net.py 1 |python3 ./net.py 2 > /tmp/f
```

Une fois les fenêtres ouvertes, on peut alors modifier le contenu textuel (qui contient au départ les explications des commandes).
Pour cela on peut entrer des commandes au format suivant : ```a;b;c```
- ```a``` est ici le numéro de ligne concernée,
- ```b``` est la commande à exécuter, on a ici :
  - ```s``` pour substituer le contenu de la ligne par le contenu définit dans ```c```
  - ```a``` pour ajouter une ligne après la ligne concernée avec le contenu défini dans ```c```
  - ```d``` pour supprimer le contenu d'une ligne. Le contenu de ```c``` n'a pas d'importance dans ce cas. 
- ```c ``` est le contenu du texte faisant l'objet de la commande. 

## Principe de fonctionnement <a class="anchor" id="Principe_de_fonctionnement"></a>

Le projet combine l'algorithme de l'activité 4, avec celui de la file d'attente et de sauvegarde. Le réseau est ici un anneau, permettant ainsi de ne pas avoir à implémenter d'algorithme de création d'anneau de contrôle.

### Activité 4 <a class="anchor" id="Activité_4"></a>

On retrouve ici la solution 6 de l'activité 4 qui consiste en l'implémentation d'une file de message gérée par un thread "centurion", et remplie d'une part par un thread de lecture dans le flux **stdin**, et de l'autre par le site voisin écrivant sur son flux **stdout** connecté à l'entrée du site. 

Étant donné que les messages sont stockés dans une file, on a donc un traitement séquentiel et FIFO de ceux-ci. Concernant la structure de celle-ci et des messages, on a dans un premier temps choisi que chaque objet de la file est un tableau de 2 cases :
- La première case est un mot qui définit quelle action faire avec le message. Si c'est "send", le message sera envoyé, si c'est "process", le message sera traité si le site est destinataire de ce message. 
- La seconde case est le contenu du message sous forme d'une chaîne de caractères. Il est nécessaire alors avant de le traiter de créer une instance de message à partir de cette chaîne de caractères. Le format des messages est presque identique à celle de Airplug, c'est-à-dire **"who\~fromWho\~messageType\~color\~isPrepost\~vectClock\~what"**. Nous avons ajouté le champs **isPrepost** et **vectClock** dans le but de ne pas avoir à le faire dans le champs **what**.


Concernant les différents acteurs de cet algorithme, on retrouve deux threads et une fonction permettant d'assurer la réception, l'envoi et le traitement des messages :
- Le centurion, dans un thread, va ici dépiler un objet de la file, lire la première case et décider alors ce que va être fait du contenu du message dans la seconde case. Lorsqu'il y a traitement du message, celui-ci est passé en paramètre de la fonction **receiveExternalMessage()** qui va réagir en fonction de son type. 
- Le thread de readMessage() lit chaque message écrit sur stdin et les enregistre sur la file(voir [documentation](#readMessage)). 
- La fonction writeMessage() permet d'envoyer le message sur le flux stdout. Le message arrive alors sur le flux stdin du site voisin de par la topologie du réseau, et donc est lu par la fonction [readMessage()](#readMessage)(voir [documentation](#writeMessage)).


### Algorithme de file d'attente <a class="anchor" id="Algorithme_de_file_d'attente "></a>

Concernant cet algorithme, on a implémenté l'algorithme disponible sur moodle (<a href="https://moodle.utc.fr/pluginfile.php/172574/mod_resource/content/1/5-POLY-file-attente-2018.pdf">Ci-contre</a>).
Pour cela, il a fallu adapter le code de l'activité 4 en ajoutant des attributs, méthodes et classes.
-  En effet, il a fallu dans un premier temps ajouter des attributs dans la classe **Net** qui sont 
    -  <u>stamp</u> : Horloge logique du site,
    -  <u>networkState</u> : État des requêtes de section critiques dans le réseaux,
- Dans un second temps ont été implémentées des méthodes permettant de gérer les requêtes et entrées en section critique : 
    - <u>basCsRequest(self)</u> : Envoie de requête d'entrée en section critique,
    - <u>basCsRelease(self)</u> : Envoie de déclaration de libération de section critique,
    - <u>checkState(self)</u> : Vérification de l'état du Site, pour éventuellement entrer en section critique,
    - <u>enterCs(self)</u> : Méthode d'entrée en section critique,
    - <u>receiveExternalLockRequestMessage(self, msgReceived)</u> : Méthode de réaction face à un message de requête d'entrée en section critique,
    - <u>receiveExternalReleaseMessage(self, msgReceived)</u> : Méthode de réaction face à un message de déclaration de libération de section critique,
    - <u>receiveExternalAckMessage(self, msgReceived)</u> : Méthode de réaction face à un message d'accusé de réception
- Dans une dernière mesure, nous avons ajouté des classes de message permettant de reconnaître des nouveaux types de messages (voir [documentation](#message)) : 
    - <u>BroadcastMessage</u> : Classe pour les messages à envoyer à tous les sites,
    - <u>LockRequestMessage</u> : Classe pour les messages de requêtes d'entrées en section critique,
    - <u>AckMessage</u> : Classe pour les messages d'accusés de réception,
    - <u>ReleaseMessage</u> : Classe pour les messages de libération de section critique.

Dès lors que ces différents outils ont été définis, il a suffit de dérouler l'algorithme défini ci-contre, notamment en définissant

### Algorithme de sauvegarde <a class="anchor" id="Algorithme_de_sauvegarde"></a>

Concernant l'algorithme de sauvegarde, il y a eu des ajouts comme dans l'algorithme de file d'attente. 
- En effet des attributs ont été ajoutés sur la classe Net, la classe State et Message: 
    - <u>initiatorSave (Net)</u>: booléen indiquant si le site est à l'initiative de la sauvegarde.
    - <u>messageAssess(State)</u> Bilan des messages en transit dans le réseau.
    - <u>globalState (Net)</u>: Dernier enregistrement de l'état global par le site,
    - <u>nbWaitingMessage (Net)</u> et <u>NbWatingState</u>: Nombre de messages et d'états attendus par le site,
    - <u>vectClock(Net et Message)</u>: Valeur de l'horloge vectorielle pour le message ou l'état.
- Ensuite, des méthodes ont été ajoutées : 
    - <u>initSnapshot(self)</u>: Méthode d'initialisation de la sauvegarde par un site,
- Enfin, des classes dans utils.py et message.py on été ajoutées: 
    - <u>VectClock</u> : classe permettant d'instancier des horloges vectorielles (voir [documentation](#VectClock)),
    - <u>SnapshotRequestMessage</u> Messages ayant comme but de transmettre les demandes de sauvegardes.
    - <u>StateMessage</u> : Messages permettant de transmettre les états des sites dans leur contenu. 

Dès lors que ces outils ont été définis, l'algorithme 11 vu dans <a href="https://moodle.utc.fr/pluginfile.php/129094/mod_resource/content/1/5-poly-06-2019S.pdf">ce cours</a> a été suivi, notamment grâce au fait que la topologie du réseau est un anneau permettant de faire office d'anneau de contrôle.

### Algorithme de l'application de base <a class="anchor" id="Algorithme_de_l'application_de_base "></a>

Pour l'application de base, nous avons choisi d'implémenter un système de partage de fichier avec un fichier partagé, accessible en lecture/écriture. Pour cela : 
- On a crée dans un premier temps une classe **Bas** dans le fichier [bas.py](/bas.py),
- On a lié une instance de **Bas** à chaque site Net dès leur construction à l'aide d'un attribut **bas**,
- A l'aide d'une interface graphique et un système de commande, l'utilisateur à la possibilité d'écrire des commandes pour commander une modification, enclenchant alors une demande d'entrée en section critique. 
- Dès que la demande est émise, le site attend son entrée en section critique. Dès son entrée, c'est-à-dire dès que **checkStatus()** déclenche **enterCs()**, qui envoie grâce à **bas.send()** un message à **Bas**, celui-ci va exécuter la commande entrée dans **doAction()**. Le fichier est modifié avec la méthode **edit()** enclenchée par **doAction()**
- Après modification du document, **Bas** envoie un message au réseau avec **sendMessageFromBas()** pour leur indiquer ce qui a été modifié. Les différents sites détectent alors un nouveau type de message **EditMessage** indiquant une modification du fichier partagé, et en réaction lancent la méthode **doAction()** avec la commande en paramètre. La modification est alors propagée. 

Pour plus de précision sur les méthodes implémentées, voir la [documentation](#BasClass) sur la classe Bas.

Concernant les méthodes ajoutées dans Net, on a: 
- <u>sendToBas(self, message)</u>: fonction qui fait appel à bas.send(self, message). Permet la transmission de messages de Net à Bas,
- <u>sendMessageFromBas(self, message)</u>: fonction qui transmet les Edit Messages aux autres sites en faisant appel à writeMessage().

Concernant les classes ajoutées, on a:
- <u>BasState ([utils.py](/utils.py))</u>: Classe permettant d'instancier des états de Bas, et de les envoyer dans les instances State lors des sauvegardes.
- <u>EditMessage ([message.py](/message.py))</u>: Messages permettant la transmission de commandes dans le réseau.
- <u>Command ([bas.py](/bas.py))</u>: Classe permettant d'instancier les commandes réalisées par les applications de base.


## Scénarios de fonctionnement <a class="anchor" id="Scenario"></a>

### Premier scénario : Ajout de contenu
 - On lance la commande de démarrage du logiciel (donné [ci-contre](#Lancement)),
 - On entre dans la section de commande le texte :
```
3;a;Ligne ajoutée
```
 - On peut alors observer l'ajout d'une ligne après la troisième ligne avec le contenu de la dernière section "Ligne ajoutée"
### Second scénario : Modification de contenu
 - On lance la commande de démarrage du logiciel (donné [ci-contre](#Lancement)),
 - On entre dans la section de commande le texte:
```
3;s;Ligne modifiée
```
 - On observe alors que la troisième ligne a été changée en "Ligne modifiée"
### Troisième scénario : Suppression de contenu
 - On lance la commande de démarrage du logiciel (donné [ci-contre](#Lancement)),
 - On entre dans la section de commande le texte:
```
3;d;Ligne supprimée
```
 - On peut alors observer la suppression de la troisième ligne dans le contenu textuel. 

### Quatrième scénario : Lancement d'une sauvegarde
- On lance la commande de démarrage du logiciel (donné [ci-contre](#Lancement)),
- On lance alors les commandes du premier et second scénario, et on clique ensuite sur le bouton ```Request a snapshot```. On observe alors que le fichier save a été créé et rempli avec différentes lignes. Celles-ci correspondent aux états des 3 sites qui ont été démarrés. L'ordre des états est ici le même que celui dans lequel les sites ont été initialisés. 
- Le format de chaque état est :
```
netId°nbSite°messageAssess°vectClock°basState
```
- ```netId``` est l'identifiant du site,
- ```nbSite``` est le nombre de site dans le réseau,
- ```messageAssess``` est le bilan des messages du site en transit dans le réseau,
- ```vectClock``` est l'horloge vectorielle du site au format ```netId#nbSite#h#h#h```, où les deux premières informations sont identiques à celles précédemment citées, et h les horloges logiques de chaque site.
- ```basState``` est l'état de l'application de base, qui est au format ```isRequestingCs°command°encodedText```, où :
  - ``ìsRequestingCS`` est le booléen indiquant si le site souhaite l'entrée en section critique, 
  - ```command``` est le contenu de la commande envoyé,
  - ``èncodedText`` est le texte envoyé, encodé en base 64.

## Documentation <a class="anchor" id="Documentation "></a>

On retrouve dans ce projet 4 fichiers :
- [net.py](/net.py) - Celui-ci contient l'ensemble de la classe Net, avec ses attributs et méthodes:
    - **Attributs** :
        - <u>netID</u> : Identifiant du site,
        - <u>nbSite</u>: Nombre de sites sur l'ensemble du réseau,
        - <u>bas</u> : Application BAS affiliée au site,
        - <u>stamp</u> : Horloge logique du site,
        - <u>networkState</u> : Tableau avec une case par site représentant leur état pour l'algorithme de la file d'attente ("R": Requête, "A" : Accusé de réception, "L" : Libéré), 
        - <u>color</u> : Couleur du site (blanc ou rouge),
        - <u>initiatorSave</u> : Booléen répondant à la question : Est-ce que ce site est l'initiateur de l'algorithme de sauvegarde ? 
        - <u>messageAssess</u> : Bilan des messages en transit dans le réseau,
        - <u>globalState</u> : État global du réseau selon ce site,
        - <u>nbWaitingMessage</u> : Nombre de messages attendus par le site,
        - <u>nbWaitingState</u> : Nombre d'états attendus par le site,
        - <u>messages</u> : File contenant l'ensemble des messages en attente de traitement. Chaque message est un tableau contenant en première case l'action à effectuer sur le message, et le contenu du message dans la seconde case.
        - <u>readMessageThread</u> : thread maintenant la fontion readMessage(),
        - <u>centurionThread</u> : thread maintenant la fonction centurion(),
        - <u>state</u> : État local du site,
    - **Méthodes**
        - <u>logger(self, logContent)</u> : Méthode d'affichage, permettant ainsi l'affichage du fonctionnement de l'algorithme sur le terminal,
        - <u>readMessage(self)</u><a class="anchor" id="readMessage"></a> : Méthode permettant, en étant lancée dans un thread, de lire l'ensemble des lignes inscrites sur stdin et de les mettre dans la file de messages,
        - <u>writeMessage(self, message)</u><a class="anchor" id="writeMessage"></a> : Méthode permettant de mettre les messages à envoyer dans la file de messages,
        - <u>centurion(self)</u><a class="anchor" id="centurion"></a> : Méthode permettant d'officier le rôle de centurion (référence à l'armée de César), en dépilant séquentiellement chaque message de la file. En fonction de la première case du message, le centurion effectue une action différente : 
            - <u>"send"</u> : Envoie le contenu du message au site voisin,
            - <u>"process"</u> : Traite le message, dans le cas où celui-ci le concerne (s'il est le destinataire du message), et le renvoie si le message concerne tous les sites, ou s'il n'est pas le destinataire du message. 
        - <u>initSnapshot(self)</u> : Méthode permettant d'initialiser la demande de sauvegarde et de la transmettre au réseau.
        - <u>sendMessageFromBas(self, message)</u> : Méthode permettant de diffuser un message reçu de BAS.
        - <u>sendToBas(self, message)</u> : Méthode permettant d'envoyer un message à BAS.
        - <u>basCsRequest(self)</u> : Envoie une requête de Section critique au réseau, et inscrit cette demande dans le tableau networkState.
        - <u>basCsRelease(self)</u> : Envoie un message de libération de la section critique au réseau et inscrit la libération dans le tableau networkState.
        - <u>checkState(self)</u> : Vérifie si le site peut entrer en section critique, en fonction de l'état du réseau dans l'algorithme de file d'attente.
        - <u>enterCs(self)</u> : Permet d'entrer en section critique, et envoie un message à Bas pour signaler l'entrée en section critique,
        - <u>receiveExternalMessage(self, msgReceived)</u> : méthode permettant la réception de message. En fonction du corps du message.  
- [bas.py](/bas.py) - Ce fichier contient l'ensemble de la Classe **Bas** et la classe **Command**, avec ses attributs et méthodes : 

- **Bas** <a class="anchor" id="BasClass"></a>
    - **Attributs** :
        - <u>net</u>: Site NET lié à l'instance BAS,
        - <u>state</u>: Contenu du fichier partagé,
        - <u>root</u>: Instance de l'interface TKinter,
        - <u>requestSnapshotButton</u>: Instance de bouton pour lancer des demandes de sauvegarde,
        - <u>printTextWidget</u>: Instance de la section de texte explicatif de l'application. 
        - <u>commandFrame</u>: Frame contenant la zone de texte ainsi que le bouton "Modifier". 
        - <u>commandEntry</u>: Instance de la zone d'entrée de texte.
        - <u>commandButton</u>: Instance contenant le bouton de modification du fichier.
    - **Méthodes** : 
        - <u>send(self, msg)</u>: Méthode permettant de lancer une instruction, contenue dans le paramètre msg, qui est soit un retour de net suite à une demande de section critique, soit une demande d'exécution reçue par NET (suite à la modification par un autre site par exemple).
        - <u>action(self)</u>: Méthode permettant d'émettre, si l'on appuie sur le bouton "Modifier", de lancer une demande de section critique sur le réseau, et de désactiver les boutons en attendant la réponse.
        - <u>doAction(self)</u>: Méthode permettant de lancer la commande contenue dans le champs de texte. Après exécution, les boutons sont à nouveau cliquables.
        - <u>edit(self, command)</u>: Méthode permettant la modification du champ texte "printTextWidget" suite à la réception d'une commande ici en paramètre.
        - <u>snapshot</u>: Méthode lancée après appui sur le bouton "Request a snapshot", lance la fonction associée de la classe Net.
        - <u>run(self)</u>: Méthode permettant de lancer l'affichage de l'interface TKinter.
- **Command**
    - **Attributs** :
        - <u>lineNumber</u>: Ligne du texte concernée par la commande.
        - <u>action</u>: Action à réaliser sur le texte (modifier/ajouter/supprimer).
        - <u>text</u>: Texte contenu de la commande (à ajouter, rempaçant le texte présent).
    - **Méthodes** :
        - <u>parse(cls, s)</u>: Méthode statique permettant de créer une instance de commande à partir d'une chaîne de caractères.


- [utils.py](/utils.py) - Ce fichier contient l'ensemble des classes utilitaires qui sont : 
    - **VectClock**<a class="anchor" id="#VectClock"></a>
        - **Attributs** :
            - <u>netID</u>: Identifiant du site visé par l'instance d'horloge vectorielle .
            - <u>nbSite</u>: Nombre de sites sur le réseau.
            - <u>clockArray</u>: Valeur de l'horloge vectorielle
        - **Méthodes** :
            - <u>incr(self, otherClock)</u>: Méthode permettant d'incrémenter l'horloge vectorielle en prenant en compte celle d'un autre site.
            - <u>__str__(self)</u>: Méthode "override" permettant d'afficher une horloge vectorielle au format "netId#nbSite#strClockArray".
            - <u>fromString(cls, stringToConvert)</u>: Méthode statique retournant une instance d'Horloge vectorielle à partir d'une chaîne de caractères.
     - **BasState** : Classe permettant d'exprimer l'état d'une application BAS
        - **Attributs** :
            - <u>text</u>: Contenu du fichier partagé par les sites au moment de la capture.
            - <u>command</u>: Contenu de la zone de texte permettant le lancement de commandes au moment de la capture.
            - <u>isRequestingCs</u>: Est-ce que l'application était en demande de section critique au moment de la capture ?
        - **Méthodes** :
            - <u>fromString(cls, stringToConvert)</u>: Méthode permettant de créer une instance de BasState à partir d'une chaîne de caractères. 
     - **State** : Classe permettant d'exprimer les états locaux des sites
        - **Attributs** :
            - <u>messageAssess</u>: Bilan des messages en transit au moment de la capture.
            - <u>netID</u>: Identifiant du site concerné par la capture.
            - <u>nbSite</u>: Nombre de sites dans le réseau.
            - <u>vectClock</u>: Horloge vectorielle du site au moment de la capture.
            - <u>basState</u>: État de l'application Bas liée au site. 
        - **Méthodes** :
            - <u>fromString(cls, stringToConvert)</u>: Créer une instance d'État à partir d'une chaîne de caractères.
            
- [messages.py](/messages.py) <a class="anchor" id="message"></a> - Ce fichier contient les différentes classes de messages, qui contiennent toutes les attributs et messages suivants:
    - **Attributs**:
        - <u>who</u>: destinataire du message,
        - <u>fromWho</u>: auteur du message,
        - <u>messageType</u>: Type du message (StateMessage, EditMessage, etc.)
        - <u>color</u>: Couleur du site émetteur du message (Blanc ou Rouge),
        - <u>isPrepost</u>: Booléen exprimant le fait que le message soit émis d'un site blanc et arrive sur un site rouge. 
        - <u>vectClock</u>: Horloge vectorielle du site émetteur du message.
        - <u>what</u>: Contenu du message.
    - **Méthodes**
        - <u>toPrepost(self)</u>: Méthode qui passe l'attribut "isPrepost" à True et retourne l'instance de Message.
        - <u>setColor(self, color)</u>: Méthode setter de l'attribut "color". 
        - <u>fromString(cls, s)</u>: Méthode créant une instance de Message à partir d'une chaîne de caractères.
    Il existe dans ce projet différents types de messages héritant de la classe Message ou de BroadcastMessage: 
        - <u>BroadcastMessage(Message)</u>: Messages ayant pour but d'être envoyés à tout le monde. 
        - <u>EditMessage(BroadcastMessage)</u>: Messages permettant de transmettre des messages permettant de modifier le contenu du fichier partagé.
        - <u>LockRequestMessage(BroadcastMessage)</u>:  Messages ayant comme but d'envoyer des requêtes d'entrées en section critique. 
        - <u>AckMessage(Message)</u>: Messages ayant pour but d'envoyer des accusés de réception.
        - <u>ReleaseMessage(BroadcastMessage)</u>: Messages ayant pour but d'envoyer des déclaration de libération de section critique.
        - <u>StateMessage(BroadcastMessage)</u>: Messages ayant pour but de transmettre des États. 
        - <u>SnapshotRequestMessage(BroadcastMessage)</u>: Messages ayant pour but d'émettre des demandes de sauvegardes.
