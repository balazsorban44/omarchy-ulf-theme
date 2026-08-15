return {
  {
    "bjarneo/aether.nvim",
    branch = "v3",
    name = "aether",
    priority = 1000,
    opts = {
      colors = {
        bg         = "#faf6f3",
        dark_bg    = "#bcb9b6",
        darker_bg  = "#7d7b7a",
        lighter_bg = "#fbf7f4",

        fg         = "#221c18",
        dark_fg    = "#1a1512",
        light_fg   = "#433e3b",
        bright_fg  = "#595552",
        muted      = "#8c857f",

        red        = "#720000",
        yellow     = "#8b6000",
        orange     = "#872626",
        green      = "#7e2913",
        cyan       = "#564241",
        blue       = "#3c342b",
        purple     = "#ad4e44",
        brown      = "#511717",

        bright_red    = "#c1624e",
        bright_yellow = "#af7c00",
        bright_green  = "#cf794b",
        bright_cyan   = "#6b5d58",
        bright_blue   = "#827271",
        bright_purple = "#c3746f",

        accent               = "#ff5a36",
        cursor               = "#221c18",
        foreground           = "#221c18",
        background           = "#faf6f3",
        selection             = "#fbf7f4",
        selection_foreground = "#221c18",
        selection_background = "#fbf7f4",
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
