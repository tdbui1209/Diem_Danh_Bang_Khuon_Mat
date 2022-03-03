
function readURL(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function (e) {
          $('#picture').attr('src', e.target.result); //.width(150).height(200)
        };
        reader.readAsDataURL(input.files[0]);
    };
};

$("#i_submit").click(function() {
    var $SCRIPT_ROOT = {{ request.script_root|tojson|safe }};
    var picture = document.getElementById("picture");
    // var img = picture.toDataURL();
    $.ajax({
        type: "POST",
        url: $SCRIPT_ROOT + "/predict/",
        data: picture.src,
        processData: false,
        success: function(data) {
            $('#result').text(data);
        }
    });
});
