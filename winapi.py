import ctypes

BIF_RETURNONLYFSDIRS = 0x0001
BIF_NEWDIALOGSTYLE = 0x0040
OFN_EXPLORER = 0x00080000
OFN_FILEMUSTEXIST = 0x00001000
OFN_HIDEREADONLY = 0x00000004
OFN_NOCHANGEDIR = 0x00000008


class BROWSEINFO(ctypes.Structure):
    _fields_ = [
        ("hwndOwner", ctypes.c_void_p),
        ("pidlRoot", ctypes.c_void_p),
        ("pszDisplayName", ctypes.c_wchar_p),
        ("lpszTitle", ctypes.c_wchar_p),
        ("ulFlags", ctypes.c_uint),
        ("lpfn", ctypes.c_void_p),
        ("lParam", ctypes.c_void_p),
        ("iImage", ctypes.c_int)
    ]


SHBrowseForFolder = ctypes.windll.shell32.SHBrowseForFolderW
SHBrowseForFolder.argtypes = [ctypes.POINTER(BROWSEINFO)]
SHBrowseForFolder.restype = ctypes.c_void_p
SHGetPathFromIDList = ctypes.windll.shell32.SHGetPathFromIDListW
SHGetPathFromIDList.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p]
SHGetPathFromIDList.restype = ctypes.c_long


class OPENFILENAME(ctypes.Structure):
    _fields_ = [
        ("lStructSize", ctypes.c_ulong),
        ("hwndOwner", ctypes.c_void_p),
        ("hInstance", ctypes.c_void_p),
        ("lpstrFilter", ctypes.c_wchar_p),
        ("lpstrCustomFilter", ctypes.c_wchar_p),
        ("nMaxCustFilter", ctypes.c_ulong),
        ("nFilterIndex", ctypes.c_ulong),
        ("lpstrFile", ctypes.POINTER(ctypes.c_wchar)),
        ("nMaxFile", ctypes.c_ulong),
        ("lpstrFileTitle", ctypes.c_wchar_p),
        ("nMaxFileTitle", ctypes.c_ulong),
        ("lpstrInitialDir", ctypes.c_wchar_p),
        ("lpstrTitle", ctypes.c_wchar_p),
        ("Flags", ctypes.c_ulong),
        ("nFileOffset", ctypes.c_ushort),
        ("nFileExtension", ctypes.c_ushort),
        ("lpstrDefExt", ctypes.c_wchar_p),
        ("lCustData", ctypes.c_long),
        ("lpfnHook", ctypes.c_void_p),
        ("lpTemplateName", ctypes.c_wchar_p),
        ("pvReserved", ctypes.c_void_p),
        ("dwReserved", ctypes.c_ulong),
        ("FlagsEx", ctypes.c_ulong)
    ]


def select_folder():
    bi = BROWSEINFO()
    bi.lpszTitle = "Select the base directory."
    bi.ulFlags = BIF_RETURNONLYFSDIRS | BIF_NEWDIALOGSTYLE
    pidl = SHBrowseForFolder(ctypes.byref(bi))
    path = ctypes.create_unicode_buffer(260)  # ctypes.wintypes.MAX_PATH = 260
    if pidl and SHGetPathFromIDList(pidl, path):
        return path.value


def select_file():
    ofn = OPENFILENAME()
    ofn.lStructSize = ctypes.sizeof(OPENFILENAME)
    buffer = ctypes.create_unicode_buffer(260)
    ofn.lpstrFile = buffer
    ofn.nMaxFile = 260
    ofn.lpstrFilter = "Cookies file\0*.json\0"
    ofn.nFilterIndex = 1
    ofn.Flags = OFN_EXPLORER | OFN_FILEMUSTEXIST | OFN_HIDEREADONLY | OFN_NOCHANGEDIR
    if ctypes.windll.comdlg32.GetOpenFileNameW(ctypes.byref(ofn)):
        return buffer.value
