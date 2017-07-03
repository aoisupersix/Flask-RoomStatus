$(window).load(init());

var hours = [];

function init() {
}
onload = function() {
  makeChart();
}

/*
 *  Jinja2経由でGETパラメータ取得
 */
function setRecord(record) {
  hours = record;
}

/*
 *  棒グラフ作成
 */
 function makeChart() {
  //hoursが空かどうか
  var kara = true;
  for(var i = 0;i<hours.length;i++){
    if(hours[i] > 0){
      kara = false;
      break;
    }
  }

  if(hours.length > 0 && !kara){
    //データ項目作成
    dataLabels = new Array(hours.length);
    for(var i=0; i<dataLabels.length;i++){
      dataLabels[i] = i + "~" + (i+1) + "時";
    }
    //合計利用者
    var sum = 0
    for(var i=0; i<hours.length;i++){
      sum += hours[i];
    }
    $("#sum").html("合計利用者:<strong>" + sum + "</strong>")

    //チャート作成
    var ctx = document.getElementById('statistics').getContext("2d");
    var myBarChart = new Chart(ctx, {
      //グラフの種類
      type: 'bar',
      //データの設定
      data: {
        //データ項目のラベル
        labels: dataLabels,
        //データセット
        datasets: [{
          //凡例
          label: "人数",
          //背景色
          backgroundColor: "rgba(75,192,192,0.4)",
          //枠線の色
          borderColor: "rgba(75,192,192,1)",
          //グラフのデータ
          data: hours
        }]
      },
      //オプションの設定
      options: {
        //軸の設定
        scales: {
          //縦軸の設定
          yAxes: [{
            //目盛りの設定
            ticks: {
              //開始値を0にする
              beginAtZero:true,
            }
          }]
        }
      }
    });
  }else {
    //空
    $("#message").html("自動では更新されません。手動で更新してください。<br><br><strong>統計情報がありません</strong>");
  }

 }
