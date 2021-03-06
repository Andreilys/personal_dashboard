var waiting_for_update = false;
// are we currently waiting?
var LONG_POLL_DURATION = 10000; // how long should we wait? (msec)
var first_time_loading = true;
var global_meditation_doughnut = Object(),
  global_pomodoro_doughnut = Object(),
  global_unproductive_doughnut = Object(),
  global_coding_chart = Object(),
  global_coding_type_chart = Object(),
  global_rescuetime_pie = Object(),
  global_rescuetime_bar = Object(),
  global_books_bar = Object(),
  global_writing_bar = Object(),
  global_meditation_bar = Object(),
  global_toggl_pie = Object(),
  global_toggl_bar = Object(),
  // global_steps_bar = Object(),
  global_weight_line = Object(),
  // global_chess_pie = Object(),
  global_cal = Object();
var POMODORO_GOAL = null;
var UNPRODUCTIVITY_GOAL = null;
var MEDITATION_GOAL = null;
/**
 * Load data from /data, optionally providing a query parameter read
 * from the #format select
 */
function load_data() {
    $.ajax({ url: '/data',
             success: function(data) {
                          display_data(data);
                      },
    });
    return true;
}


/**
 * Uses separate update notification and data providing URLs. Could be combined, but if
 * they're separated, the Python routine that provides data needn't be changed from
 * what's required for standard, non-long-polling web app. If they're combined, arguably
 * over-loads the purpose of the function.
 */
function wait_for_update() {
    if (!waiting_for_update) {
        waiting_for_update = true;
        $.ajax({ url: '/updated',
                 success:  load_data(),        // if /update signals results ready, load them!
                 complete: function () {
                    waiting_for_update = false;
                    setTimeout(wait_for_update, 5000); // if the wait_for_update poll times out, rerun
                 },
                 timeout:  LONG_POLL_DURATION,
               });
    }
}

//Used to sleep the display data so we don't have multiple threads going
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * show the data acquired by load_data()
 */
async function display_data(data) {
    if (data) {
        if (UNPRODUCTIVITY_GOAL == null){
          MEDITATION_GOAL = data.meditation_goal
          UNPRODUCTIVITY_GOAL = data.unproductivity_goal;
          POMODORO_GOAL = data.pomodoro_goal;
        }
        $('#rescue_time_past_seven_top_five').html(data.rescue_time_past_seven_top_five);
        $('#past_books').html(data.past_books);
        $('#past_writing').html(data.past_writing);
        $('#total_tasks').html("Todo List " + data.total_tasks);
        $('#top_tracks').html(data.top_tracks);
        $('#top_artists').html(data.top_artists);
        $('#temp').html(data.temp);
        $('#weather_today').html(data.weather_today);
        $('#quote_content').html(data.quote_content);
        $('#quote_author').html(data.quote_author);
        $('#moves_places').html(data.moves_places);
        // $('#chess_rating').html(data.chess_rating);
        coding_time = format_coding_data(data.coding_time);
        coding_type = format_coding_type_data(data.coding_type);
        toggl_data = format_toggl_data(data.past_seven_days_pomodoros);
        toggl_bar_data = format_toggl_data_bar(data.toggl_bar_data);
        // weight_data = format_weight_data(data.weight_line_data, data.weight_line_dates);
        rescuetime_data = format_rescuetime_data(data.rescue_time_past_seven_productivity, data.rescue_time_past_seven_unproductivity);
        // chess_pie_data = format_chess_pie_data(data.chess_games)
        if (first_time_loading) {
            global_meditation_doughnut = create_meditation_doughnut(data);
            global_pomodoro_doughnut = create_pomodoro_doughnut(data);
            global_unproductive_doughnut = create_unproductive_doughnut(data);
            global_coding_chart = create_coding_chart(coding_time);
            global_coding_type_chart = create_pie(coding_type, "coding_type");
            global_rescuetime_pie = create_pie(rescuetime_data, "rescuetime_pie")
            global_rescuetime_bar = create_bar(data.rescuetime_bar_data, data.rescuetime_bar_data_dates, "rescuetime_bar");
            global_books_bar = create_bar(data.books_bar_data, data.books_bar_data_dates, "books_bar");
            global_books_bar = create_bar(data.writing_bar_data, data.writing_bar_data_dates, "writing_bar");

            global_meditation_bar = create_bar(data.meditation_bar_data, data.meditation_bar_data_dates, "meditation_bar");
            global_toggl_pie = create_pie(toggl_data, "toggl_pie");
            //We can use rescuetime bar data dates since its the same information
            // global_steps_bar = create_bar(data.steps_bar_data, data.rescuetime_bar_data_dates, "steps_bar");
            global_toggl_bar = create_toggl_bar(toggl_bar_data);
            // global_weight_line = create_line(weight_data, "weight_line");
            // global_chess_pie = create_pie(chess_pie_data, "chess_pie");
            global_cal = create_goal_calendar();
            global_cal.update('/datesCompletedGoals');
        }
        else {
          global_cal.update('/datesCompletedGoals');
          update_doughnuts(global_meditation_doughnut, global_pomodoro_doughnut, global_unproductive_doughnut, data);
          update_coding_chart(coding_time);
          update_coding_type_chart(coding_type);
          update_pie(rescuetime_data, "rescuetime_pie", global_rescuetime_pie);
          // update_pie(chess_pie_data, "chess_pie", global_chess_pie);
          update_pie(toggl_data, "toggl_pie", global_toggl_pie);
          update_bar(data.rescuetime_bar_data, data.rescuetime_bar_data_dates, "rescuetime_bar", global_rescuetime_bar);
          //We can use rescuetime bar data dates since its the same information
          // update_bar(data.steps_bar_data, data.rescuetime_bar_data_dates, "steps_bar", global_steps_bar);
          update_bar(data.meditation_bar_data, data.meditation_bar_data_dates, "meditation_bar", global_meditation_bar);
          update_bar(data.books_bar_data, data.books_bar_data_dates, "books_bar", global_books_bar);
          update_bar(data.writing_bar_data, data.writing_bar_data_dates, "writing_bar", global_writing_bar);
          // update_line(weight_data, "weight_line", global_weight_line);
          update_toggl_bar(toggl_bar_data);
        }
        $('#loading').remove();
        $("div").css("visibility", "visible");
        $("h6").css("visibility", "visible");
      }
      if (first_time_loading){
        first_time_loading = false;
        wait_for_update();
      } else {
        await sleep(120000);
        wait_for_update();
      }
}

function create_goal_calendar(){
  calendar = new CalHeatMap();
  var dt = new Date()
  var year = dt.getYear() + 1900
  calendar.init({
      itemSelector: "#cal-heatmap",
      domain: "year",
      subDomain: "day",
      data: '/datesCompletedGoals',
      dataType: "json",
      start: new Date(year, 0),
      cellSize: 10,
      range: 1,
      displayLegend: false
  });
  return calendar;
}

//Row 1 - Start of Doughuts
function update_doughnuts(meditation_doughnut, pomodoro_doughnut, unproductive_doughnut, data) {
  var total_pomodoros = 0;
  for (var key in data.daily_doughnut_pomodoro){
    total_pomodoros += data.daily_doughnut_pomodoro[key];
  }
  var current_pomodoro_percent = total_pomodoros > POMODORO_GOAL ? 100 : Math.round(total_pomodoros/POMODORO_GOAL * 100),
      current_meditation_percent = data.current_meditation > MEDITATION_GOAL ? 100 : Math.round(data.current_meditation/MEDITATION_GOAL * 100),
      current_unproductive_percent = data.rescue_time_daily_unproductivity > UNPRODUCTIVITY_GOAL ? 100 : Math.round(data.rescue_time_daily_unproductivity/UNPRODUCTIVITY_GOAL * 100);
    //Updating meditation doughnut

      meditation_doughnut.options.title.text = String(current_meditation_percent) + "%";
      meditation_doughnut.options.data[0].dataPoints[0].y = current_meditation_percent;
      meditation_doughnut.options.data[0].dataPoints[1].y = 100 - current_meditation_percent;
      meditation_doughnut.options.data[0].dataPoints[0].toolTipContent = String(data.current_meditation) + " minutes of meditation",
    //Updating pomodoro doughnut
      pomodoro_doughnut.options.title.text = String(current_pomodoro_percent) + "%";
      pomodoro_doughnut.options.data[0].dataPoints[0].y = current_pomodoro_percent;
      pomodoro_doughnut.options.data[0].dataPoints[1].y = 100 - current_pomodoro_percent;
      pomodoro_doughnut.options.data[0].dataPoints[0].toolTipContent = String(total_pomodoros) + " hours",

    //Updating unproductivity doughnut
    unproductive_doughnut.options.title.text = String(current_unproductive_percent) + "%";
    unproductive_doughnut.options.data[0].dataPoints[0].y = current_unproductive_percent;
    unproductive_doughnut.options.data[0].dataPoints[1].y = 100 - current_unproductive_percent;
    unproductive_doughnut.options.data[0].dataPoints[0].toolTipContent= String(data.rescue_time_daily_unproductivity) + " hours",

    //Re-rendering the doughnuts
    meditation_doughnut.render();
    pomodoro_doughnut.render();
    unproductive_doughnut.render();
}


function create_pomodoro_doughnut(data){
  var total_pomodoros = 0;
  for (var key in data.daily_doughnut_pomodoro){
    total_pomodoros += data.daily_doughnut_pomodoro[key];
  }
  var current_pomodoro_percent = total_pomodoros > POMODORO_GOAL ? 100 : Math.round(total_pomodoros/POMODORO_GOAL * 100);
  var pomodoro_doughnut = new CanvasJS.Chart("pomodoro_doughnut", {
    animationEnabled: true,
    backgroundColor: "transparent",
    title: {
      fontColor: "#848484",
      fontSize: 60,
      horizontalAlign: "center",
      text: String(current_pomodoro_percent) + "%",
      fontFamily: "Roboto",
      verticalAlign: "center"
    },
    toolTip: {
      backgroundColor: "#ffffff",
      borderThickness: 0,
      cornerRadius: 0,
      fontColor: "#424242"
    },
    data: [
      {
        explodeOnClick: false,
        innerRadius: "94%",
        radius: "90%",
        startAngle: 270,
        type: "doughnut",
        dataPoints: [
          { y: current_pomodoro_percent, color: "#33702a", toolTipContent: String(total_pomodoros) + " hours"},
          { y: 100 - current_pomodoro_percent, color: "#424242", toolTipContent: null }
        ]
      }
    ]
  });

  pomodoro_doughnut.render();
  return pomodoro_doughnut;
}


function create_unproductive_doughnut(data){
  var current_unproductive_percent = data.rescue_time_daily_unproductivity > UNPRODUCTIVITY_GOAL ? 100 : Math.round(data.rescue_time_daily_unproductivity/UNPRODUCTIVITY_GOAL * 100);
  var unproductive_doughnut = new CanvasJS.Chart("unproductivity_doughnut", {
    animationEnabled: true,
    backgroundColor: "transparent",
    title: {
      fontColor: "#848484",
      fontSize: 60,
      horizontalAlign: "center",
      text: String(current_unproductive_percent) + "%",
      fontFamily: "Roboto",
      verticalAlign: "center"
    },
    toolTip: {
      backgroundColor: "#ffffff",
      borderThickness: 0,
      cornerRadius: 0,
      fontColor: "#424242"
    },
    data: [
      {
        explodeOnClick: false,
        innerRadius: "94%",
        radius: "90%",
        startAngle: 270,
        type: "doughnut",
        dataPoints: [
          { y: current_unproductive_percent, color: "#b30000", toolTipContent: String(data.rescue_time_daily_unproductivity) + " hours"},
          { y: 100 - current_unproductive_percent, color: "#424242", toolTipContent: null }
        ]
      }
    ]
  });

  unproductive_doughnut.render()
  return unproductive_doughnut;
}


//This creates and returns the meditation doughnut chart
function create_meditation_doughnut(data) {
    var current_meditation_percent = data.current_meditation > MEDITATION_GOAL ? 100 : Math.round(data.current_meditation/MEDITATION_GOAL * 100);
    var meditation_doughnut = new CanvasJS.Chart("meditation_doughnut", {
      animationEnabled: true,
      backgroundColor: "transparent",
      title: {
        fontColor: "#848484",
        fontSize: 60,
        horizontalAlign: "center",
        text: String(current_meditation_percent) + "%",
        fontFamily: "Roboto",
        verticalAlign: "center"
      },
      toolTip: {
        backgroundColor: "#ffffff",
        borderThickness: 0,
        cornerRadius: 0,
        fontColor: "#424242"
      },
      data: [
        {
          explodeOnClick: false,
          innerRadius: "94%",
          radius: "90%",
          startAngle: 270,
          type: "doughnut",
          dataPoints: [
            { y: current_meditation_percent, color: "#33702a", toolTipContent: String(data.current_meditation) + " minutes of meditation"  },
            { y: 100 - current_meditation_percent, color: "#424242", toolTipContent: null }
          ]
        }
      ]
    });
    // jQuery.inview plugin
    meditation_doughnut.render()
    return meditation_doughnut;
}


// Row 2: Start of Coding data
//Helper function to format the dates for Chartjs column graph
function changing_date_format(coding_time_unformatted){
  coding_time_formatted = []
  for (data of coding_time_unformatted){
    months_days = data['range']['date'].split('-').slice(1).join('-');
    year = data['range']['date'].split('-')[0];
    new_date = months_days + "-" + year
    data['range']['date'] = new_date
    coding_time_formatted.push(data)
  }
  return coding_time_formatted
}


function format_coding_data(coding_time_unformatted){
  coding_time_formatted = changing_date_format(coding_time_unformatted)
  coding_time = []
  for (data of coding_time_formatted) {
    coding_time.push({x: new Date(data['range']['date']), y: data['grand_total']['total_seconds']/60/60});
  }
  return coding_time
}

function format_coding_type_data(coding_type_unformated){
  coding_type = []
  for (data of coding_type_unformated) {
    coding_type.push({name: data['name'], y: data['percent'], indexLabel: String(data['name']) + " - " + String(data['percent']) + "%", legendText: data['name']});
  }
  return coding_type
}

function update_coding_chart(coding_time){
    global_coding_chart = create_coding_chart(coding_time);
    global_coding_chart.render();
}

function update_coding_type_chart(coding_type){
  global_coding_type_chart = create_pie(coding_type, "coding_type");
  global_coding_type_chart.render();
}

function create_coding_chart(coding_time) {
  var coding_chart = new CanvasJS.Chart("coding_time", {
    animationEnabled: true,
    backgroundColor: "transparent",
    theme: "theme2",
    axisX: {
      labelFontSize: 14,
      valueFormatString: "MMM DD"
    },
    axisY: {
      labelFontSize: 14,
    },
    toolTip: {
      borderThickness: 0,
      cornerRadius: 0
    },
    data: [
      {
        type: "column",
        color: "#27a6e5",
        yValueFormatString: "###,###.##",
        dataPoints: coding_time
      }
    ]
  });
  coding_chart.render();
  return coding_chart;
}


//Row 3 Rescuetime Data for pie chart
function format_rescuetime_data(rescue_time_past_seven_productivity, rescue_time_past_seven_unproductivity){
  rescuetime_weekly_data = [];
  total = rescue_time_past_seven_productivity + rescue_time_past_seven_unproductivity;
  rescuetime_weekly_data.push({name: "Productive Time", y: rescue_time_past_seven_productivity, indexLabel: "Productive Hours" + " - " + String(rescue_time_past_seven_productivity) + " (" + String((rescue_time_past_seven_productivity/total*100).toFixed(2)) + "%)", legendText: "Productive Hours"});
  rescuetime_weekly_data.push({name: "Unproductive Time", y: rescue_time_past_seven_unproductivity, indexLabel: "Unproductive Hours" + " - " + String(rescue_time_past_seven_unproductivity) + " (" + String((rescue_time_past_seven_unproductivity/total*100).toFixed(2)) + "%)", legendText: "Unproductive Hours"});
  return rescuetime_weekly_data;
}


function update_pie(data, html_id, global_var_chart){
  global_var_chart = create_pie(data, html_id);
  global_var_chart.render();
}

function create_pie(data, html_id){
  var pie = new CanvasJS.Chart(html_id, {
    animationEnabled: true,
    theme: "theme2",
    legend: {
      fontSize: 12,
      display: true,
      position: 'top',
      fullWidth: true,
      reverse: false,
    },
    toolTip: {
      borderThickness: 0,
      content: "<span style='\"'color: {color};'\"'>{name}</span>: {y}",
      cornerRadius: 0
    },
    data: [
      {
        indexLabelFontColor: "#676464",
        indexLabelFontSize: 10,
        legendMarkerType: "square",
        legendText: "{indexLabel}",
        showInLegend: true,
        startAngle:  90,
        type: "pie",
        dataPoints: data
      }
    ]
  });
  pie.render();
  return pie;
}


function update_bar(data, dates, html_id, bar_graph){
  bar_graph = create_bar(data, dates, html_id);
  bar_graph.render();
}


function create_bar(data, dates, html_id){
  var ctx = document.getElementById(html_id);
  var bar = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: dates,
      datasets: data
    },
    options: {
      animation: {
        duration: 0
      },
       barValueSpacing: 20,
       scales: {
           yAxes: [{
               ticks: {
                   min: 0,
               }
           }]
       }
     }
   });
  bar.render()
  return bar;
}


//Row 4 Toggl data
function format_toggl_data(toggl_data){
  toggl_weekly_data = [];
  total = 0;
  for (var key in toggl_data){
    total += toggl_data[key];
  }
  for (var key in toggl_data) {
    toggl_weekly_data.push({name: key, y: toggl_data[key], indexLabel: String(key) + " - " + String(toggl_data[key]) + " (" + String((toggl_data[key]/total*100).toFixed(2)) + "%)", legendText: key});
  }
  return toggl_weekly_data;
}


//
function format_toggl_data_bar(toggl_data){
  formatted_data = [];
  for (let data of toggl_data) {
    toggl_type = data.shift()
    data_points_formatted = [];
    for (let other_data of data) {
        data_points_formatted.push({x: new Date(other_data['year'], other_data['month']-1, other_data['day']), y: other_data['value']})
    }
    formatted_data.push({type:"stackedBar", legendText: toggl_type, showInLegend: "true", dataPoints: data_points_formatted})
  }
  return formatted_data;
}


function update_toggl_bar(toggl_data){
  global_toggl_bar = create_toggl_bar(toggl_data);
  global_toggl_bar.render();
}


function create_toggl_bar(toggl_data){
  var chart = new CanvasJS.Chart("toggl_bar",
    {
      axisX: {
        valueFormatString: "MMM DD"
      },
      data: toggl_data
    });
    chart.render();
    return chart;
}

//Row 4 steps and weight
// function format_weight_data(weight_data, dates){
//   formatted_dataset = []
//   dataset = []
//   for (let index in weight_data) {
//     data = {x: new Date(dates[index]), y: weight_data[index]}
//     dataset.push(data)
//   }
//   formatted_dataset.push({data: dataset, label:"Weight", borderColor: "#3e95cd", fill: false})
//   return {labels:dates, datasets: formatted_dataset}
// }


function update_line(data, html_id, global_var_chart){
  global_var_chart = create_line(data, html_id)
  global_var_chart.render()
}


function create_line(data_set, html_id){
  var line_chart = new Chart(document.getElementById(html_id), {
    type: 'line',
    data: data_set,
    options: {
            scales: {
                xAxes:
                  [{
                    time: {
                        unit: 'month'
                      }
                }]
            },
            animation: {
                duration: 0, // general animation time
            },
            hover: {
                animationDuration: 0, // duration of animations when hovering an item
            },
            responsiveAnimationDuration: 0, // animation duration after a resize
        }
  });
  line_chart.render();
  return line_chart;
}

//Row 5: Chess
// function format_chess_pie_data(chess_data){
//   chess_data_formatted = [];
//   total = chess_data['wins'] + chess_data['losses'] + chess_data['draws'];
//   chess_data_formatted.push({name: "Wins", y: chess_data['wins'], indexLabel: "Wins" + " - " + String(chess_data['wins']) + " (" + String((chess_data['wins']/total*100).toFixed(2)) + "%)", legendText: "Wins"});
//   chess_data_formatted.push({name: "Losses", y: chess_data['losses'], indexLabel: "Losses" + " - " + String(chess_data['losses']) + " (" + String((chess_data['losses']/total*100).toFixed(2)) + "%)", legendText: "Losses"});
//   chess_data_formatted.push({name: "Draws", y: chess_data['draws'], indexLabel: "Draws" + " - " + String(chess_data['draws']) + " (" + String((chess_data['draws']/total*100).toFixed(2)) + "%)", legendText: "Draws"});
//   return chess_data_formatted;
// }


function load_first_time() {
    $.ajax({ url: '/firstTimeLoad',
             success: function(data) {
                          display_data(data);
                      },
    });
    return true;
}

$(document).ready(function() {
  load_first_time()
});
