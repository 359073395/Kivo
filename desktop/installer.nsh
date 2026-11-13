!include "${PROJECT_DIR}\installer-tool.nsh"

!macro customInstall
  # NSIS CopyFiles can omit deeply nested Node.js dependencies. Extract the
  # embedded payload with native 7-Zip before reporting a successful install.
  File "/oname=$PLUGINSDIR\kivo-7z.exe" "${KIVO_7ZIP_EXTRACTOR}"
  nsExec::ExecToLog '"$PLUGINSDIR\kivo-7z.exe" x "$PLUGINSDIR\app-$packageArch.7z" "-o$INSTDIR" -y -bso0 -bsp0'
  Pop $0
  ${If} $0 != 0
    MessageBox MB_OK|MB_ICONSTOP "Kivo 文件解压失败，错误码 $0。请重新运行安装程序。" /SD IDOK
    SetErrorLevel 1
    Quit
  ${EndIf}
!macroend
