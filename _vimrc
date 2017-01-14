


filetype off
filetype plugin indent off



scriptencoding cp932
set modeline
set number
set nobackup
set noswapfile
set nocompatible
set helplang=en
set textwidth=0
set hidden
set spell spelllang=en
set encoding=utf-8
"set encoding=cp932
set termencoding=cp932
"set ambiwidth=double
set cursorline
set cursorcolumn
syntax on

cd $HOME

set makeprg=C:/Users/naoaki/app/strawberry-perl-524/c/bin/dmake
let $PATH.=";C:\\Users\\naoaki\\app\\strawberry-perl-524\\perl\\site\\bin"
let $PATH.=";C:\\Users\\naoaki\\app\\strawberry-perl-524\\perl\\bin"
let $PATH.=";C:\\Users\\naoaki\\app\\strawberry-perl-524\\c\\bin"
let $PATH.=";C:\\Users\\naoaki\\app\\PortableGit-2.11.0-64-bit.7z\\bin"

set visualbell t_vb=
set noerrorbells 

" Note: Skip initialization for vim-tiny or vim-small.
if !1 | finish | endif



" Key maps
noremap  ; :
noremap  : ;
inoremap <silent> <ESC> <ESC>
inoremap <silent> <C-[> <ESC>
inoremap <silent> <C-j> <C-^>
nnoremap <Space>,, :<C-u>edit $HOME/Desktop/scratch.py<CR>
nnoremap <Space>. :<C-u>edit $MYVIMRC<CR>
nnoremap <Space>v :<C-u>edit $MYGVIMRC<CR>
nnoremap <Space>,m :<C-u>edit $HOME/memo.txt<CR>
nnoremap <Space>,b :<C-u>edit $HOME/.cache/unite/bookmark/default<CR>
nnoremap gs :<C-u>Gstatus<CR>
nnoremap gl :<C-u>Git log -n 4 --oneline --reverse --stat<CR>
nnoremap ga :<C-u>Gwrite<CR>

inoremap <C-e> <Esc>$a
inoremap <C-a> <Esc>^a
noremap <C-e> <Esc>$a
noremap <C-a> <Esc>^a

command! ReloadVimrc source $MYVIMRC
command! ReloadGVimrc source $MYGVIMRC

" Increment and decrement
nnoremap <A-a> <C-a>
nnoremap <A-x> <C-x>

" Calender
nnoremap <Space>c :Calendar<CR>


" install dein
" cd ~/vimfiles
" git clone https://github.com/Shougo/dein.vim
" mkdir bundle

if &compatible
  set nocompatible
endif
set runtimepath+=~/vimfiles/dein.vim

call dein#begin(expand('~/vimfiles/bundle'))

call dein#add('Shougo/dein.vim')
call dein#add('Shougo/vimproc.vim', {'build': 'C:\Users\naoaki\app\strawberry-perl-524\c\bin\gmake.exe'})
call dein#add('Shougo/neocomplete.vim')
call dein#add('Shougo/neosnippet-snippets')
call dein#add('Shougo/neomru.vim')
call dein#add('Shougo/neosnippet')
call dein#add('Shougo/unite.vim')
call dein#add('Shougo/vimfiler.vim')
call dein#add('tomasr/molokai')
call dein#add('itchyny/lightline.vim')
call dein#add('itchyny/landscape.vim')
call dein#add('itchyny/calendar.vim')
call dein#add('tpope/vim-fugitive')
call dein#add('vimwiki/vimwiki')
call dein#add('thinca/vim-quickrun')
call dein#end()



" Unite
nnoremap <silent> <Space>fb :<C-u>Unite buffer<CR>
nnoremap <silent> <Space>fo :<C-u>Unite bookmark<CR>
nnoremap <silent> <Space>ff :<C-u>UniteWithBufferDir -buffer-name=files file<CR>
nnoremap <silent> <Space>fr :<C-u>Unite -buffer-name=register register<CR>
nnoremap <silent> <Space>fm :<C-u>Unite file_mru<CR>
nnoremap <silent> <Space>fv :<C-u>VimFiler<CR>
nnoremap <silent> <Space>fd :<C-u>Unite -buffer-name=files -default-action=lcd directory_mru<CR>

call unite#custom#default_action('directory' , 'vimfiler')

let g:unite_kind_file_copy_file_command        = 'c:\\Users\\naoaki\\app\\gow\\bin\\cp.exe $srcs $dest'
let g:unite_kind_file_copy_directory_command   = 'c:\\Users\\naoaki\\app\\gow\\bin\\cp.exe -r $srcs $dest'
let g:unite_kind_file_delete_file_command      = 'c:\\Users\\naoaki\\app\\gow\\bin\\rm.exe $srcs'
let g:unite_kind_file_delete_directory_command = 'c:\\Users\\naoaki\\app\\gow\\bin\\rm.exe -r $srcs'
let g:unite_force_overwrite_statusline = 0

" Vimfiler
"let g:vimfiler_as_default_explorer = 1
"let g:vimfiler_safe_mode_by_default = 0
"let g:vimfiler_force_overwrite_statusline = 0
call vimfiler#custom#profile('default', 'context', {
\   'safe' : 0
\ })


" Transparency
autocmd GUIEnter    * set transparency=240
autocmd FocusGained * set transparency=240
autocmd FocusLost   * set transparency=128
"autocmd FocusLost   * set transparency=240
nnoremap <C-Up>     :<C-u>set transparency+=20<CR>
nnoremap <C-Down>   :<C-u>set transparency-=20<CR>



let g:quickrun_config = {
\   "_" : {
\       "outputter/buffer/split" : ":botright 4sp",
\       "runner" : "system",
\   }
\}

"let g:quickrun_config.python = {'command' : 'c:\\Users\\naoaki\\app\\WinPython34\\python-3.4.4.amd64\\python.exe'}
let g:quickrun_config.python = {'command' : 'c:\\Users\\naoaki\\app\\WinPython34_32b\\python-3.4.4\\python.exe'}
"let g:quickrun_config.python = {'command' : 'c:\\Users\\naoaki\\app\\WinPython27_32b\\python-2.7.12\\python.exe'}



" My wiki
let g:vimwiki_list = [{'path': '~/Desktop/wiki/'}]


filetype plugin indent on

