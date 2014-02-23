#include <Python.h>
#include <sys/klog.h>
#include <errno.h>

#define BUF_SIZE 512

enum SYSLOG_FLAGS {
	SYSLOG_ACTION_CLOSE,	
	SYSLOG_ACTION_OPEN,
	SYSLOG_ACTION_READ,
	SYSLOG_ACTION_READ_ALL,
	SYSLOG_ACTION_READ_CLEAR,
	SYSLOG_ACTION_CLEAR,
	SYSLOG_ACTION_CONSOLE_OFF,
	SYSLOG_ACTION_CONSOLE_ON,
	SYSLOG_ACTION_CONSOLE_LEVEL,
	SYSLOG_ACTION_SIZE_UNREAD,
	SYSLOG_ACTION_SIZE_BUFFER
};

PyDoc_STRVAR(kmsg_klogctl_doc, "read and/or clear kernel message ring buffer; set console_loglevel");

static PyObject *
kmsg_klogctl(PyObject *object, PyObject *args)
{
	int flag = 0;		
	int len = 0;
	int logret = 0;
	void *buf = NULL;
	PyObject *ret = NULL;
	
	if (!PyArg_ParseTuple(args, "I|I:klogctl", &flag, &len)) {
		return NULL;
	}

	switch(flag) {
	case SYSLOG_ACTION_READ: 
		len = klogctl(SYSLOG_ACTION_SIZE_UNREAD, NULL, 0);	
		/* empty */
		if (len < 0) { 
			goto failed;
		} 
		if (len == 0) {
			ret = PyString_FromString("");
			goto finish;
		}
		buf = PyMem_Malloc(BUF_SIZE);
		if (!buf) {
			goto failed;
		} 
		logret = klogctl(flag, buf, BUF_SIZE - 1);
		if (logret < 0) {
			goto freebuf;
		} 
		ret = PyString_FromStringAndSize(buf, logret); 
		PyMem_Free(buf);
		break;
	case SYSLOG_ACTION_READ_ALL:
	case SYSLOG_ACTION_READ_CLEAR:
		len = klogctl(SYSLOG_ACTION_SIZE_BUFFER, NULL, 0);
		/* empty */
		if (len <= 0) {
			ret = PyString_FromString("");
			goto finish;
		} 
		buf = PyMem_Malloc(len + 1);
		if (!buf) {
			goto failed;
		}
		logret = klogctl(flag, buf, len);
		if (logret < 0) {
			goto freebuf;
		}
		ret = PyString_FromStringAndSize(buf, logret);
		PyMem_Free(buf);
		break; 
	case SYSLOG_ACTION_SIZE_BUFFER:
		logret = klogctl(flag, NULL, 0);
		if (logret < 0) {
			goto failed;
		}
		ret = PyInt_FromLong(logret);
		break;
	case SYSLOG_ACTION_CLEAR: 
	case SYSLOG_ACTION_CONSOLE_ON:
	case SYSLOG_ACTION_CONSOLE_OFF:
		logret = klogctl(flag, NULL, 0);	
		if (logret < 0) {
			goto failed;
		}
		Py_INCREF(Py_None);
		ret = Py_None;
		break;
	case SYSLOG_ACTION_CONSOLE_LEVEL:
		logret = klogctl(flag, NULL, len);
		if (logret < 0) {
			goto failed;
		}
		Py_INCREF(Py_None);
		ret = Py_None;
		break;
	default:
		errno = EINVAL;
		goto failed;
	}
finish:
	return ret;
freebuf:
	PyMem_Free(buf);
failed:
	PyErr_SetFromErrno(PyExc_OSError);
	return NULL;
}

static PyMethodDef kmsg_methods[] = {
	{"klogctl", (PyCFunction)kmsg_klogctl,
		METH_VARARGS, kmsg_klogctl_doc},
	{NULL, NULL, 0, NULL}
};



PyMODINIT_FUNC init_kmsg(void) {
	PyObject *m;
	m = Py_InitModule("_kmsg", kmsg_methods);
	if (m == NULL) {
		PyErr_SetString(PyExc_RuntimeError, "load module _kmsg failed");
	}
}
