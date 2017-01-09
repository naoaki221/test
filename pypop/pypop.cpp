// vim:set tabstop=4 expandtab shiftwidth=4 softtabstop=4
// vim:set foldmethod=marker:

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <iostream>

#include "Python.h"

#include "poppler-document.h"
#include "poppler-page.h"
#include "poppler-global.h"
#include "poppler-image.h"
#include "poppler-page-renderer.h"

using namespace std;

static PyObject *
version(PyObject *self)
{
#if !DBG0
    return Py_BuildValue("s", "1.0");
#else
    return Py_BuildValue("s", "1.0d");
#endif
}

#define DBG0 0

static PyObject *
render(PyObject *self, PyObject *args, PyObject *keywds)
{
#if !DBG0
    char *data;
    int length;
    int p, dpi;

    if (!PyArg_ParseTuple(args, "s#ii", &data, &length, &p, &dpi))
        return NULL;
    poppler::document *doc = poppler::document::load_from_raw_data(data, length);
    if (doc == NULL)
        return NULL;
    int num_of_pages = doc->pages();
    if (p < 0 || p >= num_of_pages)
        return NULL;

    poppler::page_renderer *r = new poppler::page_renderer();
    poppler::image image = r->render_page(doc->create_page(p), dpi, dpi);
    
    return Py_BuildValue("iiis#", image.width(), image.height(), image.bytes_per_row(),
    	image.data(), image.bytes_per_row() * image.height());
#else
    return NULL;
#endif
}

static PyObject *
get_num_of_pages(PyObject *self, PyObject *args, PyObject *keywds)
{
#if !DBG0
    char *data;
    int length;
    if (!PyArg_ParseTuple(args, "s#", &data, &length))
        return NULL;
    poppler::document *doc = poppler::document::load_from_raw_data(data, length);
    if (doc == NULL)
        return NULL;
    return Py_BuildValue("i", doc->pages());
#else
    return NULL;
#endif
}

static PyMethodDef pypop_methods[] = {
    {"version", (PyCFunction)version, METH_NOARGS, ""},
    {"render", (PyCFunction)render, METH_VARARGS | METH_KEYWORDS, ""},
    {"get_num_of_pages", (PyCFunction)get_num_of_pages, METH_VARARGS | METH_KEYWORDS, ""},
    {NULL, NULL, 0, NULL}   /* sentinel */
};

#if 1
PyMODINIT_FUNC
initpypop()
{
	Py_InitModule("pypop", pypop_methods);
}
#else
static struct PyModuleDef pypopmodule = {
    PyModuleDef_HEAD_INIT, "pypop", NULL, -1,
    pypop_methods
};

PyMODINIT_FUNC
PyInit_pypop(void)
{
    return PyModule_Create(&pypopmodule);
}
#endif

