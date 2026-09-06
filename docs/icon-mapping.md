# Icon mapping (v2)

Working list for the icon batches. Each new v2 icon lands in
`overlay/ui/src/main/resources/ui/images/overrides/<category>/<pluginId>.svg` (see
`overlay/ui/src/main/resources/ui/images/overrides/README.md`).

`kettle-ref` names the classic Kettle image used as visual reference
(`pentaho-kettle` `ui/src/main/resources/ui/images/*.png`, Apache-2.0) — shapes and
colors, never copied files.

## Status

- [x] N2a mechanism: override hook in `GuiResource` (+README resource)
- [ ] N2a core UI + perspective icons
- [ ] N2b transforms (most-used first)
- [ ] N2c actions & databases

## Transforms (N2b)

Priority batch (most-used, to be drawn first):

| Hop pluginId | kettle-ref | done |
|---|---|---|
| CSVInput | CSV.png | [ ] |
| ExcelInput | ExcelIn.png | [ ] |
| TextFileInput | TFIn.png | [ ] |
| TableInput | TIN.png | [ ] |
| TableOutput | TBL.png | [ ] |
| TextFileOutput | TFOut.png | [ ] |
| ExcelOutput | ExcelOut.png | [ ] |
| InsertUpdate | INS.png | [ ] |
| Update | UPD.png | [ ] |
| Delete | DLT.png | [ ] |
| SelectValues | SEL.png | [ ] |
| SortRows | SRT.png | [ ] |
| FilterRows | FLT.png | [ ] |
| RowGenerator | ROWGEN.png | [ ] |
| Dummy | DUM.png | [ ] |
| StreamLookup | SLKP.png | [ ] |
| DatabaseLookup | DBLKP.png | [ ] |
| DatabaseJoin | DBJ.png | [ ] |
| MergeJoin | MRGJ.png | [ ] |
| JoinRows | JOIN.png | [ ] |
| MergeRows | MERG.png | [ ] |
| GroupBy | GRP.png | [ ] |
| MemoryGroupBy | MGP.png | [ ] |
| Calculator | CAL.png | [ ] |
| Formula | FML.png | [ ] |
| Constant | CNT.png | [ ] |
| AddSequence | ADDSEQ.png | [ ] |
| GetVariable | GETVAR.png | [ ] |
| SetVariable | SETVAR.png | [ ] |
| UserDefinedJavaClass | JVC.png | [ ] |
| JavaScript | JS.png | [ ] |
| ExecSQL | ESQ.png | [ ] |
| SQLFileOutput | SFO.png | [ ] |
| Syslog | SYS.png | [ ] |
| Mail | MAIL.png | [ ] |
| HTTP | HTTP.png | [ ] |
| REST | REST.png | [ ] |
| JSONInput | JSONIn.png | [ ] |
| JSONOutput | JSONOut.png | [ ] |
| XMLInput | XMLIn.png | [ ] |

… then the long tail of remaining transforms.

## Actions (N2c)

Same pattern; kettle refs like `SQL.png`, `SHELL.png`, `MAIL.png`, `SFTP.png`,
`FTP.png`, `DEL.png`, `CPY.png`, `ZIP.png`, `EVAL.png`, `SUCCESS.png`, `START.png`.

## Databases (N2c)

One consistent series: cylinder + typical database trait, subtle color coding.
Kettle refs: `BLKMYSQL.png` (mysql), `BLKPG.png` (postgresql), `BLKORA.png` (oracle),
`BLKMSSQL.png` (mssql) — names in pentaho-kettle vary; verify against the repo.
