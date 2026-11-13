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

!macro customRemoveFiles
  # Move the whole directory on its own volume. Per-file moves into TEMP fail
  # for long dependency paths and when TEMP lives on another drive.
  SetOutPath $TEMP
  GetFullPathName $R1 "$INSTDIR\.."
  GetTempFileName $R0 "$R1"
  Delete "$R0"
  ClearErrors
  Rename "$INSTDIR" "$R0"
  ${If} ${Errors}
    Abort "无法移除旧版 Kivo，请关闭 Kivo 后重试。"
  ${EndIf}
  # Extended Windows paths retain deeply nested media dependencies.
  RMDir /r /REBOOTOK "\\?\$R0"
!macroend
