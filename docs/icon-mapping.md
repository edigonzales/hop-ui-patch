# Icon mapping (v2)

Working list for the icon batches. Each new v2 icon lands in
`overlay/ui/src/main/resources/ui/images/overrides/<category>/<pluginId>.svg` (see
`overlay/ui/src/main/resources/ui/images/overrides/README.md`).

`kettle-ref` names the classic Kettle image used as visual reference
(`pentaho-kettle` `ui/src/main/resources/ui/images/*.png`, Apache-2.0) — shapes and
colors, never copied files.

## Status

- [x] N2a mechanism: override hook in `GuiResource` (+README resource)
- [x] N2a core UI + perspective icons (24 icons in `overlay/ui/.../ui/images/`):
      folder, execution, metadata, gear, plugin, terminal, show-results,
      hide-results, add, open, save, save-as, undo, redo, copy, paste, cut,
      search, close, delete, select-all, unselect-all, shutdown, image
- [x] N2b transforms, first batch (40 icons in
      `overlay/ui/.../ui/images/overrides/transforms/`): CSVInput, ExcelInput,
      TextFileInput2, TableInput, TableOutput, TextFileOutput,
      TypeExitExcelWriterTransform, JsonInput, JsonOutput, XMLInputStream,
      GetVariable, Rest, Http, SystemInfo, StreamLookup, DBLookup, DBJoin,
      DimensionLookup, MergeJoin, JoinRows, MergeRows, GroupBy, MemoryGroupBy,
      SelectValues, SortRows, FilterRows, RowGenerator, Dummy, Calculator,
      Formula, Constant, Sequence, SetVariable, UserDefinedJavaClass,
      ScriptValueMod, ExecSql, SQLFileOutput, SwitchCase, WriteToLog, Unique
- [x] N2b transforms, second batch (59 icons): Abort, AddXML,
      AdvancedXMLOutput, AnalyticQuery, Append, BlockingTransform,
      BlockUntilTransformsFinish, ChangeFileEncoding, CheckSum, CloneRow,
      Coalesce, ColumnExists, CombinationLookup, ConcatFields,
      CreditCardValidator, DataGrid, Delay, Denormaliser, DetectEmptyStream,
      DetectLastRow, DynamicSqlRow, EnhancedJsonOutput, ExecInfo, ExecProcess,
      FieldSplitter, FieldsChangeSequence, FileExists, FileLocked, Flattener,
      FuzzyMatch, GetFileNames, IfNull, Janino, JavaFilter, JdbcMetadata,
      LoadFileInput, MetaInject, Normaliser, NullIf, NumberRange, ProcessFiles,
      PropertyInput, PropertyOutput, RegexEval, ReplaceString, SampleRows,
      SchemaMapping, SetValueConstant, SetValueField, SplitFieldToRows3,
      StringCut, StringOperations, TableCompare, TableExists, ValueMapper,
      WebServiceAvailable, WebServiceLookup, YamlInput, ZipFile
- [ ] N2b transforms, long tail (remaining ~70)
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
