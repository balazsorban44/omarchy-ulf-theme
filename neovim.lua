return {
  {
    "bjarneo/aether.nvim",
    branch = "v3",
    name = "aether",
    priority = 1000,
    opts = {
      colors = {
        bg         = "#0d0b09",
        dark_bg    = "#0a0807",
        darker_bg  = "#070605",
        lighter_bg = "#252322",

        fg         = "#d7d3d0",
        dark_fg    = "#a19e9c",
        light_fg   = "#dddad7",
        bright_fg  = "#e1dedc",
        muted      = "#827c77",

        red        = "#dc4506",
        yellow     = "#ffb000",
        orange     = "#e1612b",
        green      = "#d57059",
        cyan       = "#b7a993",
        blue       = "#7d7969",
        purple     = "#f06400",
        brown      = "#873a1a",

        bright_red    = "#f78f00",
        bright_yellow = "#ffdb74",
        bright_green  = "#ffaa71",
        bright_cyan   = "#f5e1d8",
        bright_blue   = "#a19186",
        bright_purple = "#ffb7a7",

        accent               = "#ff5a36",
        cursor               = "#d7d3d0",
        foreground           = "#d7d3d0",
        background           = "#0d0b09",
        selection             = "#252322",
        selection_foreground = "#d7d3d0",
        selection_background = "#252322",
      },
    },
  },
  {
    "LazyVim/LazyVim",
    opts = {
      colorscheme = "aether",
    },
  },
}
