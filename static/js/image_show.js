function displayImg(input, imgElement) {
    var file = input.files[0];
    var reader = new FileReader();

    reader.onload = function(e) {
        imgElement.attr('src', e.target.result);
    }

    reader.readAsDataURL(file);
}
