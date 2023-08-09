function showExifTable(seedV, stepsV, samplerV, cfg_scaleV, model_hashV, clip_skipV, denoising_strengthV) {
    // 이미지를 클릭하면 호출되는 함수입니다.

    // 테이블을 표시할 div 요소를 가져옵니다.
    var exifTableDiv = document.getElementById("exifTable");

    // 현재 테이블의 상태를 가져옵니다.
    var tableDisplay = exifTableDiv.style.display;

    if (tableDisplay === "block") {
        // 이미 테이블이 보이는 상태라면 숨깁니다.
        exifTableDiv.style.display = "none";
    } else {
        // 테이블이 숨겨져 있는 상태라면 표시합니다.

        // exif 정보를 저장한 변수를 가져옵니다. (예: exifData)
        var exifData = {
            seed : seedV,
            steps : stepsV,
            sampler : samplerV,
            cfg_scale : cfg_scaleV,
            model_hash : model_hashV,
            clip_skip : clip_skipV,
            denoising_strength : denoising_strengthV
        };

        // 테이블 내용을 작성합니다.
        var tableHTML = "<table>";
        for (var key in exifData) {
            tableHTML += "<tr><td>" + key + "</td><td>" + exifData[key] + "</td></tr>";
        }
        tableHTML += "</table>";

        // 테이블 div에 내용을 삽입하고 표시합니다.
        exifTableDiv.innerHTML = tableHTML;
        exifTableDiv.style.display = "block";
    }
}