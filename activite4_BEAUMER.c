// gcc activite4_BEAUMER.c -o prog -l pthread

#include <stdio.h>
#include <unistd.h>
#include <pthread.h>
#define MAX_LEN 50

pthread_mutex_t lock; //mutex pour garantir l'atomicité
char s[MAX_LEN]; //entrée sur stdin

void *comm_stdout()  //traité par le thread 1, message périodique sur stdout
{
    pid_t pid = getpid();
    int cpt = 1;
    while (1) {
        pthread_mutex_lock(&lock); //verrouillage du mutex
        printf("pid %d message periodique %d\n", pid, cpt);
        cpt++;
        fflush(stdout);
        pthread_mutex_unlock(&lock); //on libère l'exclusivité
        sleep(1);
    }
}

void *recep_stderr()  //traité par le thread 2, réception sur stdin et écriture sur stderr
{
    pid_t pid = getpid();
    while (1) {
        if (fgets(s, MAX_LEN, stdin)) { //si saisie sur stdin,
            pthread_mutex_lock(&lock); //on verrouille le mutex
            //vérification de l'atomicité : décommenter les 2 lignes suivantes
            //fprintf(stderr, "pid %d blocage pour l'atomicité\n", pid);
            //sleep(3) //
            fprintf(stderr, "pid %d réception dans stderr :%s\n", pid, s); //réécriture du message sur stderr
            fflush(stderr);
            pthread_mutex_unlock(&lock); //libération du mutex
        }
    }
}

int main(int argc, char *argv[])
{
    pthread_t tid[2]; //tableau des id threads
    int err;//gestion des erreurs

    //initialisation du mutex
    if (pthread_mutex_init(&lock, NULL) != 0) {
        printf("\nproblème init mutex\n");
        return 1;
    }

    //gestion des erreurs de création des threads
    err = pthread_create(&(tid[0]), NULL, &comm_stdout, NULL);
    if (err != 0)
        printf("\nimpossible de lancer le message périodique");

    err = pthread_create(&(tid[1]), NULL, &recep_stderr, NULL);
    if (err != 0)
        printf("\nimpossible de créer la saisie");

    //attente de la fin des threads avant de détruire le mutex
    pthread_join(tid[0], NULL);
    pthread_join(tid[1], NULL);
    pthread_mutex_destroy(&lock);
    return 0;
}

