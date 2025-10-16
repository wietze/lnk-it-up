
#define INITGUID
#include <windows.h>
#include <shobjidl.h>
#include <shlguid.h>
#include <initguid.h>
#include <tchar.h>
#include <stdio.h>
#include <objbase.h>

int main(int argc, char *argv[])
{
    CoInitialize(NULL);
    HRESULT hres;
    IShellLink *psl;
    IPersistFile *ppf;

    bool verbose = stricmp(argv[2],"-v") == 0;

    // Create IShellLink
    hres = CoCreateInstance(CLSID_ShellLink, NULL, CLSCTX_INPROC_SERVER, IID_IShellLink, (LPVOID *)&psl);
    if (SUCCEEDED(hres))
    {
        if(verbose) printf("[+] created\n");
    }
    else
    {
        printf("[-] NOT CREATED: %d", hres);
        exit(2);
    }
    // Get a pointer to the IPersistFile interface.
    hres = psl->QueryInterface(IID_IPersistFile, (void **)&ppf);
    if (SUCCEEDED(hres))
    {
        if(verbose) printf("[+] queried\n");
    }
    else
    {
        printf("[-] NOT QUERIED\n");
        exit(2);
    }
    // Load LNK file
    WCHAR wsz[MAX_PATH];

    // Ensure that the string is Unicode.
    MultiByteToWideChar(CP_ACP, 0, argv[1], -1, wsz, MAX_PATH);
    hres = ppf->Load(wsz, STGM_READ);
    if (SUCCEEDED(hres))
    {
        if(verbose) printf("[+] loaded\n");
    }
    else
    {
        printf("[-] NOT LOADED: %d\n", hres);
        exit(2);
    }

    WIN32_FIND_DATA wfd2;
    char szPath2[MAX_PATH]; // Declare an LPSTR buffer
    hres = psl->GetPath(szPath2, MAX_PATH, (WIN32_FIND_DATA *)&wfd2, SLGP_RAWPATH);

    hres = psl->Resolve(NULL, SLR_NO_UI | SLR_NOUPDATE | SLR_NOLINKINFO);
    if (SUCCEEDED(hres))
    {
        if(verbose) printf("[+] resolved\n");
    }
    else
    {
        printf("[-] NOT RESOLVED: %d\n", hres);
        exit(2);
    }

    WIN32_FIND_DATA wfd;
    char szPath[MAX_PATH]; // Declare an LPSTR buffer
    hres = psl->GetPath(szPath, MAX_PATH, (WIN32_FIND_DATA *)&wfd, 0);

    char szArgs[MAX_PATH]; // Declare an LPSTR buffer
    hres = psl->GetArguments(szArgs, MAX_PATH);
    if (SUCCEEDED(hres))
    {
        if(verbose) printf("[+] parsed\n");
    }
    else
    {
        printf("[-] NOT PARSED: %d\n", hres);
        exit(2);
    }

    ppf->Release();
    if(verbose) printf("Original: %s|\n", szPath2);

    char szPath2_exp[MAX_PATH]; // Declare an LPSTR buffer
    DWORD size = ExpandEnvironmentStringsA(szPath2, szPath2_exp, MAX_PATH);
    if (size == 0) printf("[-] NO EXPANSION");
    if(verbose) printf("Expected: %s|\n", szPath2_exp);

    if(verbose) printf("Resolved: %s|\n", szPath);

    if (stricmp(szPath, szPath2_exp) != 0)
    {
        printf("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! WARNING\n");
    }
    if(verbose) printf("Argument: %s\n\n", szArgs);
    psl->Release();

    if (stricmp(szPath, szPath2) != 0)
    {
        exit(1);
    }
    else
    {
        exit(0);
    }
}
