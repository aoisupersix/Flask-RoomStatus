$(window).load(init());

function init() {
  update();
  /*
   *任意人数追加モーダルビュー
   */
  $(document).on('click', "#addNum-Accept", function() {
    $("#addNumModal").modal('hide');
    var num = $("#InputAddNum").val();
    add(num);
  });
  /*
   *任意時刻追加モーダルビュー
   */
  $(document).on('click', "#addTime-Accept", function() {
    $("#addTimeModal").modal('hide');
    var input = $("#InputTime").val();
    var match = input.match(/^(\d{1,2}):(\d{1,2}):(\d{1,2})$/);
    if(!match){
      alert("入力された値は不正です。");
    }else{
      var addDate = new Date();
      addDate.setHours(parseInt(match[1]));
      addDate.setMinutes(parseInt(match[2]));
      addDate.setSeconds(parseInt(match[3]));
      var time = JSON.stringify({
        "unixtime": Math.floor(addDate.getTime() / 1000)
      });
      $.ajax({
        type: 'POST',
        url:'/addTime',
        data: time,
        contentType: 'application/json',
        success:function(ret){updateLayout(ret);}
      });
    }
  });

  /*
   *手動追加ドロップダウンクリック
   */
  $(document).on('click', "li.DropDown-Add", function() {
    var index = $('li.DropDown-Add').index(this);
    switch(index){
      case 0:
        //1追加
        add(1);
        break;
      case 1:
        //任意追加
        //モーダルビュー表示
        $("#addNumModal").modal('show');
        break;
      case 2:
        //時刻追加
        //モーダルビュー表示
        $("#addTimeModal").modal('show');
        var now = new Date();
        $("#nowday").text(now.getFullYear() + "/" + (now.getMonth() + 1) + "/" + now.getDay());
        $("#InputTime").val(now.getHours() + ":" + now.getMinutes() + ":" + now.getSeconds());
        break
    }
  });

  /*
   *手動削除ドロップダウンクリック
   */
  $(document).on('click', "li.DropDown-Remove", function() {
    var index = $('li.DropDown-Remove').index(this);
    switch(index){
      case 0:
        //1削除
        remove(REMOVE_ONE);
        break
      case 1:
        //全削除
        remove(REMOVE_ALL);
        break
    }
  })
}

/*
 * 2秒ずつ更新する
 */
 function update() {
   add(0);
   setTimeout(function() {update()}, 2000);
 }

/*
 *  レスポンス -> レイアウト更新
 *  ret:レスポンス
 */
function updateLayout(ret) {
  var cap = JSON.parse(ret.ResultSet).capacity;
  var inroomNum = JSON.parse(ret.ResultSet).inRoomNum;
  var inRoom = JSON.parse(ret.ResultSet).inRoom;
  var percent = Math.round((parseFloat(inroomNum) / parseInt(cap)) * 100);
  $("#inRoomNum").text(inroomNum);
  $("#capacity").text(cap);
  $("#utilization").text(percent);
  //テーブル削除
  $("#roomStatus").find("tr:gt(0)").remove();
  //テーブル追加
  for(var i = 0; i < inRoom.length; i++){
    $("#roomStatus").append(
      $("<tr></tr>")
        .append($("<th></th>").text(i))
        .append($("<td></td>").text(inRoom[i]))
    );
  }
}

/*
 *  サーバにnum人AddPOSTする
 *  n:追加する人数
 */
function add(n) {
  var num = JSON.stringify({"num": n});
  $.ajax({
    type: 'POST',
    url:'/add',
    data: num,
    contentType: 'application/json',
    success:function(ret){updateLayout(ret);}
  });
}

/*
 * サーバにnum人RmPOSTする
 * n:
 *  REMOVE_ONE:1人削除
 *  REMOVE_ALL:全削除
 */
 let REMOVE_ONE = 0
 let REMOVE_ALL = 1
 function remove(n) {
   var num = JSON.stringify({"num": n});
   $.ajax({
     type: 'POST',
     url:'/rm',
     data: num,
     contentType: 'application/json',
     success:function(ret){updateLayout(ret);},
     error:function(XMLHttpRequest, textStatus, errorThrown){
       //エラー
     }
   });
 }
