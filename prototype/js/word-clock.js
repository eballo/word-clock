  // Change the strings below to reflect your planned grid.
  // Make sure all strings are the same length.
  // Any spaces will be replaced with random characters from RANDCHARS.
  // 16x16
  var row_strs = [
    " ÉSÓN VORA      ",
    " UN DOS TRES    ",
    " QUARTS         ",
    " IMENYS CINC    ",
    " DED'LA LES     ",
    " UNADUESTRES    ",
    " QUATRE CINC    ",
    " SISSETVUIT     ",
    " NOU DEUONZE    ",
    " DOTZE          ",
    "    EN PUNT     ",
    " IMENYS CINC    ",
    "    MINUTS      ",
    " DELLA TARDA    ",
    " LA NITMATÍ     ",
    "                ",
  ];
  var NUM_ROWS = row_strs.length;
  var NUM_COLS = row_strs[0].length;

  // Code below replaces spaces in the text grid above with random chars.
  // This is easier than adding random chars manually when you're experimenting.
  // Change RANDCHARS if you want a different set of letters in your grid."
  var RANDCHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
  for (r = 0; r < NUM_ROWS; r++) {
    chars = row_strs[r].split('');
    for (var c = 0; c < chars.length; c++) {
      if (chars[c] == ' ') {
        chars[c] = RANDCHARS.charAt(Math.floor(Math.random() * RANDCHARS.length));
      }
    }
    row_strs[r] = chars.join("");
  }

  function rowColToId(row_num, col_num) {
    return "row" + row_num + ",col" + col_num;
  }

  // Function to dim all letters in the grid.
  function dimAll() {
    for (c = 0; c < NUM_COLS; c++) {
      for (r = 0; r < NUM_ROWS; r++) {
        document.getElementById(rowColToId(r, c)).style.color = "#1a1a1a";
      }
    }
  }

  // Function to highlight a single letter.
  function highlightLetter(row_num, col_num) {
    document.getElementById(rowColToId(row_num, col_num)).style.color = "white";
  }

  // Function finds the first instance of a word in the grid, and highlights it.
  function highlightWord(w) {
    return highlightWordFrom(w, 0, 0);
  }

  // Function finds and highlights a word, starting the search at first_row/first_col.
  function highlightWordFrom(w, first_row, first_col) {
    for (var row_num = first_row; row_num < NUM_ROWS; row_num++) {
      row_str = row_strs[row_num];
      i = row_str.indexOf(w, first_col);
      first_col = 0; // for the next row
      if (i != -1) {
        for (offset = 0; offset < w.length; offset++) {
          highlightLetter(row_num, i + offset);
        }
        var col_num = i + offset;
        return {
          row_num,
          col_num
        };
      }
    };
    // Didn't find it
    row_num = 0;
    var col_num = 0;
    return {
      row_num,
      col_num
    };
  }

  // Call this function to light up a full sentence in the grid.
  function highlightWords(words) {
    var first_row = 0;
    var first_col = 0;
    word_array = words.split(" ");
    word_array.forEach(function(word, i) {
      resp = highlightWordFrom(word, first_row, first_col);
      first_row = resp.row_num;
      first_col = resp.col_num;
    });
  }

  // This function converts a Date object to a sentence.
  var ARTICLES = ["ÉS LA", "SÓN LES", "SÓN"]
  var PREPOSITON = ["DE", "D'"]
  var HOUR_WORDS = ["DOTZE", "UNA", "DUES", "TRES", "QUATRE", "CINC",
    "SIS", "SET", "VUIT", "NOU", "DEU", "ONZE", "DOTZE"
  ];
  var MINUTE_WORDS = ["EN PUNT", "I CINC", "UN QUART MENYS CINC", "UN QUART",
    "UN QUART I CINC", "DOS QUARTS MENYS CINC", "DOS QUARTS", "DOS QUARTS I CINC",
    "TRES QUARTS MENYS CINC", "TRES QUARTS", "TRES QUARTS I CINC", "MENYS CINC"
  ];

  function dateToSentence(d) {
    var hour = d.getHours();
    var minutes = Math.floor(d.getMinutes() / 5)
    if(minutes >= 2 && minutes <= 10){
      hour = hour + 1
    }


    if (hour == 1) {
      articles = ARTICLES[0];
    } else {
      articles = ARTICLES[1];
    }
    if(hour == 1 || hour == 11 || hour - 12 == 11){
      preposition = PREPOSITON[1];
    }else{
      preposition = PREPOSITON[0];
    }
    if (hour < 12) {
      hour_words = HOUR_WORDS[hour];
      am_pm = "DEL MATÍ";
    } else if (hour < 18) {
      hour_words = HOUR_WORDS[hour - 12];
      am_pm = "DE LA TARDA";
    } else {
      hour_words = HOUR_WORDS[hour - 12];
      am_pm = "DE LA NIT";
    }

    var minute_words = MINUTE_WORDS[minutes];
    if (minutes>0 && !( minutes == 1 || minutes == 11)){
      articles = ARTICLES[2];
    }

    if(minutes == 0 || minutes == 1 || minutes == 11){
      sentence = articles + " " + hour_words + " " + minute_words + " " + " " + am_pm;
    }else{
      sentence = articles + " " + minute_words + " " + preposition + " " + " " + hour_words + " " + am_pm;
    }

    return sentence
  }

  // Setup: create one HTML "tile" for each letter in the grid
  var panel = document.getElementById("word-clock");
  row_strs.forEach(function(row_str, row_num) {
    for (i = 0; i < row_str.length; i++) {
      n = document.createElement("div");
      n.setAttribute("class", "tile");
      n.setAttribute("id", rowColToId(row_num, i));
      n.textContent = "" + row_str.charAt(i);
      panel.appendChild(n);
    };
    n = document.createElement("div");
    n.setAttribute("class", "tilebreak");
    panel.appendChild(n);
  });

  // Whenever this method is called, it gets the current time,
  // converts it to a sentence, and displays it on the grid.
  function updateTime() {
    dimAll();
    var sentence = dateToSentence(new Date());
    console.log(sentence);
    highlightWords(sentence);
  }

  // Render the current time, and set a timer to re-do it every 10 seconds.
  updateTime();
  //window.setInterval(updateTime, 10000);

  window.setInterval(demo, 3000);

  // This is the code that reads the hh:mm time on <enter>,
  // parses it, and displays it.
  var text_entry_field = document.getElementById("ad_hoc_time");

  function alertAboutInputError() {
    alert("Only hh::mm in the text field");
  }
  text_entry_field.onkeypress = function(event) {
    if (event.keyCode == 13) {
      pieces = text_entry_field.value.split(":");
      if (pieces.length != 2) {
        alertAboutInputError();
        return;
      }
      hrs = parseInt(pieces[0]);
      mins = parseInt(pieces[1]);
      if (isNaN(hrs) || isNaN(mins)) {
        alertAboutInputError();
        return;
      }
      update_clock(hrs, mins);
    }
  };

  function update_clock(hrs, mins){
    hd = new Date(2020, 7, 7, hrs, mins, 0, 0);
    s = dateToSentence(hd);
    console.log(s)
    dimAll();
    highlightWords(s);
  }

  function demo(){
    hrs = Math.floor(Math.random() * 24);
    mins = Math.floor(Math.random() * 60);
    update_clock(hrs, mins);
  }
