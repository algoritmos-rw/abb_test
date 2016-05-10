#!/usr/bin/env python2
# coding: utf-8

from __future__ import print_function

import itertools
import operator
import random
import subprocess
import sys
import unittest

CMD_NAME = "./abb_aux"


def gen_trees(n):
  """Genera todas las estructuras de ABB de N nodos.

  El primer árbol devuelto es [1, 2, ..., n]. Los siguientes árboles son las
  permutaciones justas que representan todas las posibles estructuras de ABBⁿ.

  Algoritmo extraído de:

      http://www.stringology.org/event/2009/psc09p17_presentation.pdf

  """
  assert n < 10
  xs = [x for x in range(1, n + 1)]

  def next_tree():
    for i in range(n - 2, -1, -1):  # Tamaño del working suffix.
      for j in range(n - 1, i, -1):
        if xs[i] == xs[j] - 1:
          xs[i], xs[j] = xs[j], xs[i]
          xs[i+1:] = sorted(xs[i+1:])
          return xs

  while xs:
    yield list(xs)
    xs = next_tree()


class TestABB(unittest.TestCase):
  """Prueba inserciones, borrados y reemplazos de árboles de tamaño 7.

  No prueba:

    - obtener/pertenece/borrar de claves que no existen (!)

    - operaciones guardar/borrar/remplazar entremezcladas (!)

    - destructor de datos

    - claves de más de un caracter (!)
  """
  def test1_insertar(self):
    for tree in gen_trees(7):
      self.reset()
      self.check_insertar(tree)
    self.msg = None

  def test2_borrar(self):
    for ins_tree in gen_trees(5):
      for del_keys in gen_trees(5):
        self.reset()
        self.check_borrar(del_keys, ins_tree)
    self.msg = None

    for ins_tree in gen_trees(7):
      self.reset()
      del_keys = list(ins_tree)
      random.shuffle(del_keys)
      self.check_borrar(del_keys, ins_tree)
    self.msg = None

  def test3_reemplazar(self):
    replace_order = sorted(range(1, 8))
    for ins_tree in gen_trees(7):
      self.reset()
      random.shuffle(replace_order)
      self.check_reemplazar(replace_order, ins_tree)
    self.msg = None

  # Funciones auxiliares.

  def check_insertar(self, tree):
    for i, key in enumerate(tree):
      fmt = " ".join(map(str, tree[:i+1]))

      self.msg = ("\nFalló abb_guardar({}, {})\n"
                  "en la secuencia de inserción: {} <==="
                  .format(key, val(key), fmt))
      self.assertTrue(self.guardar(key))

      self.msg = ("\nFalló abb_cantidad() tras insertar: " + fmt)
      self.assertEqual(i+1, self.cantidad())

      self.msg = ("\nFalló abb_pertenece({})\n"
                  "tras haber insertado: {}".format(key, fmt))
      self.assertTrue(self.pertenece(key))

      self.msg = ("\nFalló abb_obtener({})\n"
                  "tras haber insertado: {}".format(key, fmt))
      self.assertEqual(val(key), self.obtener(key))

  def check_borrar(self, del_keys, ins_tree):
    tam = len(ins_tree)
    fmt_ins = " ".join(map(str, ins_tree))

    for key in ins_tree:
      self.msg = ("\nFalló el paso abb_guardar({}, {})\n"
                  "en la creación del árbol: {}".format(key, val(key), fmt_ins))
      self.assertTrue(self.guardar(key))

    for i, key in enumerate(del_keys):
      fmt = " ".join(map(str, del_keys[:i+1]))
      self.msg = ("\nFalló abb_borrar({})\n"
                  "tras la secuencia de borrado: {} <===\n"
                  "habiendo insertado: {}".format(key, fmt, fmt_ins))
      self.assertEqual(val(key), self.borrar(key))
      self.msg = ("\nFalló abb_cantidad()\n"
                  "tras la secuencia de borrado: {} <===\n"
                  "habiendo insertado: {}".format(fmt, fmt_ins))
      tam -= 1
      self.assertEqual(tam, self.cantidad())

  def check_reemplazar(self, repl_order, ins_tree):
    fmt = " ".join(map(str, repl_order))
    fmt_ins = " ".join(map(str, ins_tree))

    for key in ins_tree:
      self.msg = ("\nFalló el paso abb_guardar({}, {})\n"
                  "en la creación del árbol: {}".format(key, val(key), fmt_ins))
      self.assertTrue(self.guardar(key))

    for key in repl_order:
      self.msg = ("\nFalló el reemplazo abb_guardar({}, {})\n"
                  "tras haber insertado la secuencia: {}"
                  .format(key, val2(key), fmt_ins))
      self.assertTrue(self.reemplazar(key))

    for key in repl_order:
      self.msg = ("\nFalló abb_obtener({})\n"
                  "tras haber insertado: {}\n"
                  "al ir reemplazando: {} <===".format(key, fmt_ins, fmt))
      self.assertEqual(val2(key), self.obtener(key))

  # Funciones internas.

  def guardar(self, key):
    self.seq.append(("G", key))
    return bool(self._communicate("G", key))

  def borrar(self, key):
    self.seq.append(("B", key))
    return self._communicate("B", key)

  def cantidad(self):
    return self._communicate("C")

  def pertenece(self, key):
    return bool(self._communicate("P", key))

  def obtener(self, key):
    return self._communicate("O", key)

  def reemplazar(self, key):
    self.seq.append(("R", key))
    return bool(self._communicate("R", key))

  def reset(self):
    self.seq = []
    return self._communicate("X")

  def _communicate(self, cmd, key=""):
    self.proc.stdin.write("{}{}\n".format(cmd, key))
    self.proc.stdin.flush()

    line = self.proc.stdout.readline()
    self.proc.poll()

    if self.proc.returncode is not None:
      self.fail("Murió el proceso abb_aux")
    else:
      ok, val = line.split(" ", 1)
      return int(val)

  def setUp(self):
    self.seq = []
    self.proc = subprocess.Popen(["valgrind", CMD_NAME],
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)

  def tearDown(self):
    self.proc.poll()
    r = self.proc.returncode

    if r:
      print("\n\nABB MURIÓ{}\n{}\n".format(" CON SEGMENTATION FAULT"
                                           if r == -11 else "", self.msg),
            file=sys.stderr)
      sys.stderr.write(self.proc.stderr.read())
    else:
      self.proc.stdin.close()
      self.proc.wait()

    if self.msg:
      print(self.msg, file=sys.stderr)


class TestLeaks(TestABB):
  """Mismas pruebas, pero con detector de leaks en Valgrind.

  Solo se ejecuta si las anteriores pasaron.
  """
  def setUp(self):
    self.seq = []
    self.proc = subprocess.Popen(["valgrind", "--leak-check=full",
                                  "--track-origins=yes", CMD_NAME],
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)


def val(x):
  return x + ord("0")


def val2(x):
  return val(x) * 2


if __name__ == "__main__":
  unittest.main(failfast=True, verbosity=2)
