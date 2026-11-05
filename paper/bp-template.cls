\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{bp-template}

% ------------------------------
% Document Class
% ------------------------------
\LoadClass[10pt,letter,twoside]{article}

% ------------------------------
% Package Imports 
% ------------------------------
\usepackage[utf8]{inputenc}
\usepackage[margin=1in]{geometry}

\usepackage{xcolor}
\definecolor{SPred}{HTML}{d01c32}
\definecolor{SPgrey}{HTML}{79797C}
\colorlet{dkblue}{cyan!50!gray}
\definecolor{dkgreen}{rgb}{0,0.6,0}

\usepackage{graphicx}
\usepackage{float}
\usepackage{color}
\usepackage{booktabs}
\usepackage{amsmath}
\usepackage{amsfonts}
\usepackage{array}
\usepackage{tabularx}
\usepackage{lscape}
\usepackage{tikz}
\usepackage{circuitikz}
\usepackage{eurosym}
\usepackage{lipsum}
\usepackage{adjustbox}

% Paragraph handling FIRST
\usepackage{parskip}

% Alignment / justification (must come AFTER parskip)
\usepackage{ragged2e}

\usepackage{enumitem}
\usepackage[most]{tcolorbox}
\tcbuselibrary{skins}

\usepackage{caption}
\usepackage{subcaption}

\usepackage[
  authordate,
  autocite=inline,
  backend=bibtex,
  natbib
]{biblatex-chicago}

\usepackage{hyperref}

% ------------------------------
% Hyperref Configuration 
% ------------------------------
\hypersetup{
    colorlinks=true,
    linkcolor=SPred,
    citecolor=SPgrey,
    filecolor=SPred,
    urlcolor=SPred
}

% ------------------------------
% Bibliography
% ------------------------------
\bibliography{DPE_library.bib}

% ------------------------------
% Fonts
% ------------------------------
\renewcommand{\familydefault}{\sfdefault}

% ------------------------------
% GLOBAL JUSTIFICATION FIX (CRITICAL)
% ------------------------------
\AtBeginDocument{%
  \setlength{\emergencystretch}{3em} % required for sans-serif justification
  \justifying
}

\AddToHook{cmd/section/before}{\justifying}
\AddToHook{cmd/subsection/before}{\justifying}
\AddToHook{cmd/subsubsection/before}{\justifying}
\AddToHook{cmd/paragraph/before}{\justifying}
\AddToHook{cmd/subparagraph/before}{\justifying}

% ------------------------------
% Captions
% ------------------------------
\captionsetup{
  font=small,
  labelfont=bf,
  labelsep=period,
  justification=centering
}

% ------------------------------
% Lists
% ------------------------------
\setlist[description]{
  leftmargin=0pt,
  labelsep=0.75em,
  itemsep=0.5em,
  topsep=0.5em,
  font=\bfseries
}

% ------------------------------
% Section formatting
% ------------------------------
\renewcommand\section{\@startsection {section}{1}{\z@}%
  {-3.5ex \@plus -1ex \@minus -.2ex}%
  {0.2ex \@plus.2ex}%
  {\sffamily\bfseries}}

\renewcommand\subsection{\@startsection{subsection}{2}{\z@}%
  {-3.25ex\@plus -1ex \@minus -.2ex}%
  {0.2ex \@plus .2ex}%
  {\sffamily\bfseries\itshape}}

\renewcommand\subsubsection{\@startsection{subsubsection}{3}{\z@}%
  {-3.25ex\@plus -1ex \@minus -.2ex}%
  {0.2ex \@plus .2ex}%
  {\sffamily\itshape}}

\renewcommand\paragraph{\@startsection{paragraph}{4}{\z@}%
  {3.25ex \@plus1ex \@minus.2ex}%
  {-1em}%
  {\sffamily}}

\renewcommand\subparagraph{\@startsection{subparagraph}{5}{\parindent}%
  {3.25ex \@plus1ex \@minus .2ex}%
  {-1em}%
  {\sffamily}}

\def\@hangfrom#1{\setbox\@tempboxa\hbox{{#1}}%
  \hangindent 0pt
  \noindent\box\@tempboxa}

% ------------------------------
% Title helpers
% ------------------------------
\newcommand{\leftalignedtitle}[1]{%
  \noindent\raggedright\textbf{\Large #1}\par
}

\newcommand{\leftalignedauthor}[1]{%
  \noindent\raggedright #1\par
}

% ------------------------------
% Keywords
% ------------------------------
\newcommand{\keywords}[1]{%
  \noindent\textbf{Keywords:} #1
}
\newcommand{\jel}[1]{%
  \noindent\textbf{JEL Code:} #1
}

% ------------------------------
% Abstract box
% ------------------------------
\tcbset{
  abstractset/.style={
    colback=gray!10,
    colframe=white,
    sharp corners,
    boxrule=0pt,
    left=1em,
    right=1em,
    top=1em,
    bottom=1em,
    width=\textwidth
  }
}

\newcommand{\abs}[1]{%
  \begin{tcolorbox}[abstractset]
    #1
  \end{tcolorbox}
}

% ------------------------------
% Notation box
% ------------------------------
\tcbset{
  notationbox/.style={
    enhanced,
    colback=blue!5,
    colframe=blue!40!black,
    coltitle=black,
    title=Notation,
    fonttitle=\bfseries,
    boxrule=0.8pt,
    sharp corners,
    top=6pt,
    bottom=6pt,
    left=6pt,
    right=6pt,
    before skip=10pt,
    after skip=10pt
  }
}

\newcommand{\notationblock}[1]{%
  \begin{tcolorbox}[notationbox]
    #1
  \end{tcolorbox}
}

% ------------------------------
% Markdown-style boxes
% ------------------------------
\tcbset{
  markdownquote/.style={
    blanker,
    borderline west={2pt}{0pt}{gray},
    left=1em,
    top=0.5em,
    bottom=0.5em
  }
}

\newcommand{\mdquote}[1]{%
  \begin{tcolorbox}[markdownquote]
    #1
  \end{tcolorbox}
}

% ------------------------------
% Info / warning / code boxes
% ------------------------------
\tcbset{
  warnbox/.style={
    colback=red!5,
    colframe=red!50,
    boxrule=0.4pt,
    sharp corners,
    left=1em,
    right=1em
  }
}

\newcommand{\warn}[1]{%
  \begin{tcolorbox}[warnbox]
    \textbf{Remark.} #1
  \end{tcolorbox}
}

\tcbset{
  infobox/.style={
    colback=blue!5,
    colframe=blue!50,
    boxrule=0.4pt,
    sharp corners,
    left=1em,
    right=1em
  }
}

\newcommand{\info}[1]{%
  \begin{tcolorbox}[infobox]
    \textbf{Note:} #1
  \end{tcolorbox}
}

\tcbset{
  codeblock/.style={
    colback=black!5,
    colframe=black!20,
    boxrule=0pt,
    fontupper=\ttfamily\footnotesize,
    sharp corners,
    left=1em,
    right=1em
  }
}

\newcommand{\codeblock}[1]{%
  \begin{tcolorbox}[codeblock]
    #1
  \end{tcolorbox}
}

\newtheorem{definition}{Definition}[section] 
\newtheorem{proposition}{Proposition}[section]
\newtheorem{assumption}{Assumption}[section] 
\newtheorem{lemma}{Lemma}[section]
\newtheorem{proof}{Proof}[section]
\newtheorem{corollary}{Corollary}[section]

% ------------------------------
% Misc
% ------------------------------
\newcommand{\divider}{\vspace{1em}\hrule\vspace{1em}}

\renewcommand{\theequation}{Eq.~\arabic{equation}}

\RequirePackage{lastpage}
\RequirePackage[online]{threeparttable}
\RequirePackage{endnotes}

\newcommand*{\printendnotes}{%
  \def\enoteformat{\rightskip=0pt \leftskip=0pt \parindent=0pt \makeenmark}
  \def\makeenmark{\bgroup\bfseries\theenmark\enspace\egroup}
  \theendnotes
}