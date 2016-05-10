#define _POSIX_C_SOURCE 200809L  // getline()

#include "abb.h"

#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/*
 * Realiza una serie de operaciones leídas por entrada estándar.
 */
int main(void) {
  size_t tam = 0;
  char *linea = NULL;

  abb_t *abb = abb_crear(strcmp, NULL);

  while (getline(&linea, &tam, stdin) >= 0) {
    const char *key = linea + 1;
    void *val;
    intptr_t ival = *key;

    switch (*linea) {
    case 'G':
      // Guardar
      printf("OK %d\n", abb_guardar(abb, key, (void*) ival));
      break;

    case 'B':
      // Borrar
      val = abb_borrar(abb, key);
      printf("OK %" PRIiPTR "\n", (intptr_t) val);
      break;

    case 'R':
      // Reemplazar
      printf("OK %d\n", abb_guardar(abb, key, (void*) (ival*2)));
      break;

    case 'O':
      // Obtener
      val = abb_obtener(abb, key);
      printf("OK %" PRIiPTR "\n", (intptr_t) val);
      break;

    case 'P':
      // Pertenece
      printf("OK %d\n", abb_pertenece(abb, key));
      break;

    case 'C':
      // Cantidad
      printf("OK %zu\n", abb_cantidad(abb));
      break;

    case 'X':
      // Reset.
      abb_destruir(abb);
      abb = abb_crear(strcmp, NULL);
      puts("OK 1");
      break;

    default:
      fprintf(stderr, "Instrucción no reconocida: %s\n", linea);
    }
    fflush(stdout);
  }
  free(linea);
  abb_destruir(abb);
  return 0;
}
