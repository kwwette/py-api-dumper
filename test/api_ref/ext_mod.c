/*
 * SPDX-FileCopyrightText: 2025 Karl Wette
 *
 * SPDX-License-Identifier: MIT
 */

#include <Python.h>

/// public extension module ///

static PyObject *do_task(PyObject *self, PyObject *args) {
  Py_RETURN_NONE;
}

static PyObject *do_something(PyObject *self, PyObject *args) {
  Py_RETURN_NONE;
}

static PyMethodDef methods[] = {
  { "do_task", do_task, METH_VARARGS, "Do a task" },
  { "do_something", do_something, METH_VARARGS, "do_something(a, b, c)\n--\n\nDo something" },
  { NULL, NULL, 0, NULL }
};

static PyModuleDef module = {
  PyModuleDef_HEAD_INIT,
  "ext_mod",
  "External module",
  -1,
  methods
};

PyMODINIT_FUNC PyInit_ext_mod(void) {
  return PyModule_Create(&module);
}
