'''
Created on Apr 8",u"2013

@author: himanshu
'''

stopwords = set([u"a",u"able",u"about",u"above",u"according",u"accordingly",u"across", u"actually",u"after",u"afterwards",u"again",u"against",u"ain't",u"all",
             "allow",u"allows",u"almost",u"alone",u"along",u"already",u"also",u"although",u"always",u"am",u"among",u"amongst",u"an",u"and",u"another",u"any",
             "anybody",u"anyhow",u"anyone",u"anything",u"anyway",u"anyways",u"anywhere",u"apart",u"appear",u"appreciate",u"appropriate",u"are",u"aren't",
             "around",u"as",u"aside",u"ask",u"asking",u"associated",u"at",u"available",u"away",u"awfully",u"be",u"became",u"because",u"become",u"becomes",
             "becoming",u"been",u"before",u"beforehand",u"behind",u"being",u"believe",u"below",u"beside",u"besides",u"best",u"better",u"between",u"beyond",
             "both",u"brief",u"but",u"by",u"c'mon",u"c's",u"came",u"can",u"can't",u"cannot",u"cant",u"cause",u"causes",u"certain",u"certainly",u"changes",
             "clearly",u"co",u"com",u"come",u"comes",u"concerning",u"consequently",u"consider",u"considering",u"contain",u"containing",u"contains",
             "corresponding",u"could",u"couldn't",u"course",u"currently",u"definitely",u"described",u"despite",u"did",u"didn't",u"different",u"do",
             "does",u"doesn't",u"doing",u"don't",u"done",u"down",u"downwards",u"during",u"each",u"edu",u"eg",u"eight",u"either",u"else",u"elsewhere",
             "enough",u"entirely",u"especially",u"et",u"etc",u"even",u"ever",u"every",u"everybody",u"everyone",u"everything",u"everywhere",u"ex",
             "exactly",u"example",u"except",u"far",u"few",u"fifth",u"first",u"five",u"followed",u"following",u"follows",u"for",u"former",u"formerly",
             "forth",u"four",u"from",u"further",u"furthermore",u"get",u"gets",u"getting",u"given",u"gives",u"go",u"goes",u"going",u"gone",u"got",u"gotten",
             "greetings",u"had",u"hadn't",u"happens",u"hardly",u"has",u"hasn't",u"have",u"haven't",u"having",u"he",u"he's",u"hello",u"help",u"hence",u"her",
             "here",u"here's",u"hereafter",u"hereby",u"herein",u"hereupon",u"hers",u"herself",u"hi",u"him",u"himself",u"his",u"hither",u"hopefully",u"how",
             "howbeit",u"however",u"i'd",u"i'll",u"i'm",u"i've",u"ie",u"if",u"ignored",u"immediate",u"in",u"inasmuch",u"inc",u"indeed",u"indicate",u"indicated",
             "indicates",u"inner",u"insofar",u"instead",u"into",u"inward",u"is",u"isn't",u"it",u"it'd",u"it'll",u"it's",u"its",u"itself",u"just",u"keep",u"keeps",
             "kept",u"know",u"knows",u"known",u"last",u"lately",u"later",u"latter",u"latterly",u"least",u"less",u"lest",u"let",u"let's",u"like",u"liked",u"likely",
             "little",u"look",u"looking",u"looks",u"ltd",u"mainly",u"many",u"may",u"maybe",u"me",u"mean",u"meanwhile",u"merely",u"might",u"more",u"moreover",u"most",
             "mostly",u"much",u"must",u"my",u"myself",u"name",u"namely",u"nd",u"near",u"nearly",u"necessary",u"need",u"needs",u"neither",u"never",u"nevertheless",u"new",
             "next",u"nine",u"no",u"nobody",u"non",u"none",u"noone",u"nor",u"normally",u"not",u"nothing",u"novel",u"now",u"nowhere",u"obviously",u"of",u"off",u"often",u"oh",
             "ok",u"okay",u"old",u"on",u"once",u"one",u"ones",u"only",u"onto",u"or",u"other",u"others",u"otherwise",u"ought",u"our",u"ours",u"ourselves",u"out",u"outside",
             "over",u"overall",u"own",u"particular",u"particularly",u"per",u"perhaps",u"placed",u"please",u"plus",u"possible",u"presumably",u"probably",u"provides",
             "que",u"quite",u"qv",u"rather",u"rd",u"re",u"really",u"reasonably",u"regarding",u"regardless",u"regards",u"relatively",u"respectively",u"right",u"said",
             "same",u"saw",u"say",u"saying",u"says",u"second",u"secondly",u"see",u"seeing",u"seem",u"seemed",u"seeming",u"seems",u"seen",u"self",u"selves",u"sensible",
             "sent",u"serious",u"seriously",u"seven",u"several",u"shall",u"she",u"should",u"shouldn't",u"since",u"six",u"so",u"some",u"somebody",u"somehow",u"someone",
             "something",u"sometime",u"sometimes",u"somewhat",u"somewhere",u"soon",u"sorry",u"specified",u"specify",u"specifying",u"still",u"sub",u"such",u"sup",u"sure",
             "t's",u"take",u"taken",u"tell",u"tends",u"th",u"than",u"thank",u"thanks",u"thanx",u"that",u"that's",u"thats",u"the",u"their",u"theirs",u"them",u"themselves",
             "then",u"thence",u"there",u"there's",u"thereafter",u"thereby",u"therefore",u"therein",u"theres",u"thereupon",u"these",u"they",u"they'd",u"they'll",u"they're",
             "they've",u"think",u"third",u"this",u"thorough",u"thoroughly",u"those",u"though",u"three",u"through",u"throughout",u"thru",u"thus",u"to",u"together",u"too",u"took",
             "toward",u"towards",u"tried",u"tries",u"truly",u"try",u"trying",u"twice",u"two",u"un",u"under",u"unfortunately",u"unless",u"unlikely",u"until",u"unto",u"up",
             "upon",u"us",u"use",u"used",u"useful",u"uses",u"using",u"usually",u"value",u"various",u"very",u"via",u"viz",u"vs",u"want",u"wants",u"was",u"wasn't",u"way",u"we",
             "we'd",u"we'll",u"we're",u"we've",u"welcome",u"well",u"went",u"were",u"weren't",u"what",u"what's",u"whatever",u"when",u"whence",u"whenever",u"where",
             "where's",u"whereafter",u"whereas",u"whereby",u"wherein",u"whereupon",u"wherever",u"whether",u"which",u"while",u"whither",u"who",u"who's",u"whoever",
             "whole",u"whom",u"whose",u"why",u"will",u"willing",u"wish",u"with",u"within",u"without",u"won't",u"wonder",u"would",u"would",u"wouldn't",u"yes",u"yet",
             "you",u"you'd",u"you'll",u"you're",u"you've",u"your",u"yours",u"yourself",u"yourselves",u"zero"])


