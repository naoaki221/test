//
// coding: cp932
// vim: set tabstop=8 expandtab shiftwidth=4 softtabstop=4:
// vim: set foldmethod=marker:

#include <winsock2.h>
#include <iphlpapi.h>
#include <icmpapi.h>
#include <stdio.h>

#include "Python.h"

#define DBG0 0

static PyObject *
ping(PyObject *self, PyObject *args, PyObject *keywds)
{
#if !DBG0
    char *target_ip;
    int length;

    if (!PyArg_ParseTuple(args, "s#", &target_ip, &length))
        return NULL;

    HANDLE hIcmpFile;
    unsigned long ipaddr = INADDR_NONE;
    DWORD dwRetVal = 0;
    char SendData[32] = "Data Buffer";
    LPVOID ReplyBuffer = NULL;
    DWORD ReplySize = 0;

    ipaddr = inet_addr(target_ip);
    if (ipaddr == INADDR_NONE) {
        return NULL;
    }

    hIcmpFile = IcmpCreateFile();
    if (hIcmpFile == INVALID_HANDLE_VALUE) {
        return NULL;
    }    

    ReplySize = sizeof(ICMP_ECHO_REPLY) + sizeof(SendData);
    ReplyBuffer = (VOID*) malloc(ReplySize);
    if (ReplyBuffer == NULL) {
        return NULL;
    }    

    dwRetVal = IcmpSendEcho(hIcmpFile, ipaddr, SendData, sizeof(SendData), 
            NULL, ReplyBuffer, ReplySize, 1000);
    if (dwRetVal != 0) {
        PICMP_ECHO_REPLY pEchoReply = (PICMP_ECHO_REPLY)ReplyBuffer;
        struct in_addr ReplyAddr;
        ReplyAddr.S_un.S_addr = pEchoReply->Address;
        inet_ntoa(ReplyAddr);
        return Py_BuildValue("sii", inet_ntoa(ReplyAddr), pEchoReply->Status, pEchoReply->RoundTripTime);
    }
    else {
        return NULL;
    }
#else
    return NULL;
#endif
}

static PyMethodDef ping_methods[] = {
    {"ping", (PyCFunction)ping, METH_VARARGS | METH_KEYWORDS, ""},
    {NULL, NULL, 0, NULL}   /* sentinel */
};

static struct PyModuleDef pingmodule = {
    PyModuleDef_HEAD_INIT, "ping", NULL, -1,
    ping_methods
};

PyMODINIT_FUNC
PyInit_ping(void)
{
    return PyModule_Create(&pingmodule);
}

