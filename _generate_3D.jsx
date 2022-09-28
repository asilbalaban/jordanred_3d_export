// Adobe Illustrator Export (3D sunum için export scripti)
var document = app.activeDocument;
productId = app.activeDocument.textFrames.getByName("productId").contents

var exportOptions = new ExportOptionsJPEG();
exportOptions.artBoardClipping = true;
exportOptions.antiAliasing = true;
exportOptions.qualitySetting = 100;

scaleTo = 24.91
if (scaleTo) {
    exportOptions.verticalScale = scaleTo;
    exportOptions.horizontalScale = scaleTo;
}

var today = new Date();
var date = today.getFullYear() + '-' + (today.getMonth()+1) + '-' + today.getDate();
var time = today.getHours() + "-" + today.getMinutes() + "-" + today.getSeconds();
var date_time = date + '-' + time;

document.exportFile(File("~/asilme/jordanred_3d_export/folder_export/"+date_time+"__"+productId+".jpg"), ExportType.JPEG, exportOptions);

var runFile = File("~/asilme/jordanred_3d_export/upload.py")
runFile.execute();

// alert("Başarılı bir şekilde kaydedildi.");