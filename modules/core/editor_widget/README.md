# Editor Widget readme

## Alterations provided

 - editor_widget_init
 - editor_init
 - editor_configure
 - editor_presave
 - editor_save

## Workflow alterations

 - editor_init -> editor_config -> editor_widget_init
 - editor_presave (called before anything) -> editor_save (called after saving the file)
 