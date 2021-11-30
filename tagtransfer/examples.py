
EXAMPLES = [

      {
        "input": "foo",
        "expectedPlainString": "foo",
        "translation": "foo",
        "expectedProjectedString": "foo",
      },
      {
        "input": "foo bar",
        "expectedPlainString": "foo bar",
        "translation": "foo bar",
        "expectedProjectedString": "foo bar",
      },
      {
        "input": "<b>foo</b> bar",
        "expectedPlainString": "foo bar",
        "translation": "foo bar",
        "expectedProjectedString": "<b>foo</b> bar",
      },
      {
        "input": "<b>foo</b>bar",
        "expectedPlainString": "foobar",
        "translation": "foobar",
        "expectedProjectedString": "<b>foobar</b>",
      },
      {
        "input": "<b>foo</b> bar",
        "expectedPlainString": "foo bar",
        "translation": "bar foo",
        "expectedProjectedString": "<b>bar</b> foo",
      },
      {
        "input": "<b>foo</b> bar one two three",
        "expectedPlainString": "foo bar one two three",
        "translation": "bar foo uno",
        "expectedProjectedString": "<b>bar</b> foo uno",
      },
      {
        "input": "foo bar one two <b>three</b>",
        "expectedPlainString": "foo bar one two three",
        "translation": "bar foo uno",
        "expectedProjectedString": "bar foo uno<b></b>",
      },
      {
        "input": "<b>foo</b> bar one",
        "expectedPlainString": "foo bar one",
        "translation": "bar foo uno dos tres",
        "expectedProjectedString": "<b>bar</b> foo uno dos tres",
      },
      {
        "input": "foo bar <b>one</b>",
        "expectedPlainString": "foo bar one",
        "translation": "bar foo uno dos tres",
        "expectedProjectedString": "bar foo <b>uno dos tres</b>",
      },
      {
        "input": "<div><b>foo</b> bar one two three</div>",
        "expectedPlainString": "foo bar one two three",
        "translation": "bar foo uno",
        "expectedProjectedString": "<div><b>bar</b> foo uno</div>",
      },
      {
        "input": "<div>foo bar one two <b>three</b></div>",
        "expectedPlainString": "foo bar one two three",
        "translation": "bar foo uno",
        "expectedProjectedString": "<div>bar foo uno<b></b></div>",
      },
      {
        "input": "<div><b>foo</b> bar one</div>",
        "expectedPlainString": "foo bar one",
        "translation": "bar foo uno dos tres",
        "expectedProjectedString": "<div><b>bar</b> foo uno dos tres</div>",
      },
      {
        "input": "<div>foo bar <b>one</b></div>",
        "expectedPlainString": "foo bar one",
        "translation": "bar foo uno dos tres",
        "expectedProjectedString": "<div>bar foo <b>uno</b> dos tres</div>",
      },
      {
        "input": "<br><b>foo</b> bar one<br>",
        "expectedPlainString": " foo bar one ",
        "translation": "bar foo uno dos tres",
        "expectedProjectedString": "<br><b>bar</b> foo uno dos tres<br>",
      },
      {
        "input": "<b>foo</b> bar <a>one</a>",
        "expectedPlainString": "foo bar one",
        "translation": "bar foo uno dos tres",
        "expectedProjectedString": "<b>bar</b> foo <a>uno dos tres</a>",
      },
      {
        "input": "<b>foo</b> <a>bar</a> one",
        "expectedPlainString": "foo bar one",
        "translation": "bar foo uno dos tres",
        "expectedProjectedString": "<b>bar</b> <a>foo</a> uno dos tres",
      },
      {
        "input": "<b>foo</b>.",
        "expectedPlainString": "foo.",
        "translation": "bar.",
        "expectedProjectedString": "<b>bar.</b>",
      },
      {
        "input": '<div id="n0"><b id="n1">Hola</b> mundo</div>',
        "expectedPlainString": "Hola mundo",
        "translation": "Hello world",
        "expectedProjectedString":
          '<div id="n0"><b id="n1">Hello</b> world</div>',
      },
      {
        "input": '<div id="n0"><b id="n1">Bienvenidos</b> a Wikipedia,</div>',
        "expectedPlainString": "Bienvenidos a Wikipedia,",
        "translation": "Welcome to Wikipedia,",
        "expectedProjectedString":
          '<div id="n0"><b id="n1">Welcome</b> to Wikipedia,</div>',
      },
      {
        "input": '<div id="n0"><br>artículos<b id="n1"> en español</b>.</div>',
        "expectedPlainString": " artículos en español.",
        "translation": "articles in Spanish.",
        "expectedProjectedString":
          '<div id="n0"><br>articles<b id="n1"> in Spanish.</b></div>',
      },
      {
        "input":
          "<div id=n0><br><b id=n1>(hace 400 años)</b>: En Estados Unidos, se firma el <b id=n2>Pacto del Mayflower</b>, que establece un Gobierno.</div>",
        "expectedPlainString":
          " (hace 400 años): En Estados Unidos, se firma el Pacto del Mayflower, que establece un Gobierno.",
        "translation":
          "(400 years ago): In the United States, the Mayflower Pact, which establishes a government, is signed.",
        "expectedProjectedString":
          '<div id="n0"><br><b id="n1">(400 years ago):</b> In the United States, the Mayflower Pact, <b id="n2">which establishes a</b> government, is signed.</div>',
      },
      {
        "input":
          "<div id=n2> la enciclopedia de contenido libre<br>que <b id=n3>todos pueden editar</b>. </div>",
        "expectedPlainString":
          " la enciclopedia de contenido libre que todos pueden editar. ",
        "translation": "the free content encyclopedia that everyone can edit.",
        "expectedProjectedString":
          '<div id="n2"> the free content encyclopedia that<br>everyone <b id="n3">can edit.</b></div>',
      },
      {
        "input":
          "<div id=n0><br><b id=n1>(hace 50 años)</b>: Fallece <b id=n2>Chandrasekhara Raman</b>, físico indio (n. 1888; <b id=n3>en la imagen</b>), premio Nobel de física en 1930.</div>",
        "expectedPlainString":
          " (hace 50 años): Fallece Chandrasekhara Raman, físico indio (n. 1888; en la imagen), premio Nobel de física en 1930.",
        "translation":
          "(50 years ago): Chandrasekhara Raman, Indian physicist, dies (n 1888; in pictures), Nobel laureate in 1930.",
        "expectedProjectedString":
          '<div id="n0"><br><b id="n1">(50 years ago):</b> Chandrasekhara Raman, <b id="n2">Indian physicist,</b> dies (n 1888; in pictures), <b id="n3">Nobel laureate in</b> 1930.</div>',
      },
      {
        "input": "In early 2018, security researchers disclosed two major vulnerabilities, known as <a href=\"https://en.wikipedia.org/wiki/Meltdown_(security_vulnerability)\" target=\"_blank\">Meltdown</a> and <a href=\"https://en.wikipedia.org/wiki/Spectre_(security_vulnerability)\" target=\"_blank\">Spectre</a>",
        "expectedPlainString": "",
        "translation": "",
        "expectedProjectedString": ""
      }
]
