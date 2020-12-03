
#use "tag-parser.ml";;
open Reader;;

exception X_syntax_error;;

exception Incorrect_arg_error;;
exception Out_of_bound_index;;

let input = Tag_Parser.tag_parse_expressions {};;


let rec is_proper_list s =
   match s with
   |Pair(a, b) -> if b = Nil then true else (is_proper_list b)
   |Nil -> true
   |_-> false;;


let car s =
  match s with
  |Pair(a, b) -> a
  |_ -> raise X_syntax_error;;

let cdr s =
  match s with
  |Pair(a, b) -> b
  |_ -> raise X_syntax_error;;


let is_pair s =
  match s with
   |Pair(a, b) -> true
   |_-> false;;
let is_seq s =
  is_pair s && (car s) = (Symbol ("begin"));;

let is_symbol s =
  match s with
   |Symbol(a) -> true
   |_-> false;;


let get_symbol_name s =
  match s with
  |Symbol(a) -> a
  |_-> raise Incorrect_arg_error;;

let list_length s =
  let rec loop lst len =
    match lst with
    |Pair(a, b) -> if b = Nil
                   then (len +1)
                   else (loop (cdr lst) (len + 1))
    |Nil -> 0
    |_-> raise Incorrect_arg_error in
  loop s 0;;


let all_list_length s =

  let rec loop lst len =
    match lst with
    |Pair(a, b) -> (loop (cdr lst) (len + 1))
    |Nil -> len
    |_-> len + 1 in
  let initial_loop lst =
    match lst with
    |Pair(a, b)-> (loop lst 0)
    |Nil -> 0
    |_-> raise Incorrect_arg_error in
  initial_loop s ;;


let list_scheme_to_list s =
  let rec loop lst = if all_list_length lst = 0
                     then []
                     else (car lst)::(loop (cdr lst)) in

  loop s;;



let list_scheme_to_list_im s =
  let rec loop lst = if all_list_length lst = 2
                     then [car lst; Symbol "." ; cdr lst]
                     else (car lst)::(loop (cdr lst)) in

  loop s;;

let rec to_scheme sexp =
  match sexp with
  |Number( Int (a)) -> string_of_int a
  |Number(Float(a)) -> string_of_float a
  |Char(a) -> list_to_string [a]
  |Symbol(a) ->  a

  |String(a) -> a
  |Bool(a) when a -> "true"
  |Bool(a) -> "false"
  |Nil -> "()"
  |Pair(a,b) when a = Symbol("quote") && (is_proper_list b) ->  String.concat "" ["'";to_scheme (car b)]
  |Pair(a,b) when a = Symbol("quote") &&  (not (is_proper_list b)) ->  String.concat "" ["'";to_scheme  b]
  |Pair(a,b) ->  let head = [to_scheme a] in

                 let tail = match b with
                   |Nil -> []
                   |_ when is_proper_list b -> List.map to_scheme (list_scheme_to_list b)
                   |_ when not (is_pair b) -> ["." ;to_scheme b]
                   |_ ->  List.map to_scheme  (list_scheme_to_list_im b) in
                 String.concat " " (List.concat [["("];head;tail;[")"]])

  |Vector (a) -> let lst =  List.map to_scheme a in
                 String.concat " " (List.concat [["#("];lst;[")"]]);;

let to_scheme_wrapper sexp= match sexp with
  |Pair(a,b)  -> String.concat "" ["'";to_scheme sexp]
  |Symbol(a) -> String.concat "" ["'";to_scheme sexp]
  |_ -> to_scheme sexp;;


let to_list_scheme str =
  String.concat " " (List.concat [["("];str;[")"]]);;

let rec to_scheme2 expr =
  match expr with
  |Const (a) when a = Void -> "Void"
  |Const (Sexpr(a)) -> to_scheme_wrapper a
  |Var(a) -> a
  |If(a,b,c) -> to_list_scheme ["if";to_scheme2 a;to_scheme2 b;to_scheme2 c]
  |Seq (lst) -> to_list_scheme (List.concat [["begin"];List.map to_scheme2 lst])
  |Set(a,b) ->  to_list_scheme (List.concat [["set!"];[to_scheme2 a];[to_scheme2 b]])
  |Def(a,b) ->  to_list_scheme (List.concat [["define"];[to_scheme2 a];[to_scheme2 b]])
  |Or(lst) -> to_list_scheme (List.concat [["or"];List.map to_scheme2 lst])
  |LambdaSimple(args , body) -> to_list_scheme (List.concat [["lambda"];[(to_list_scheme args)];(match body with
                                                                                                 |Seq(lst) -> List.map to_scheme2 lst
                                                                                                 |_ ->  [to_scheme2 body])])

  |LambdaOpt(arg1,arg2,body) when List.length arg1 = 0 -> to_list_scheme (List.concat [["lambda"];[arg2];(match body with
                                                                                                                        |Seq(lst) -> List.map to_scheme2 lst
                                                                                                                        |_ ->  [to_scheme2 body])])

  |LambdaOpt(arg1,arg2,body) -> to_list_scheme (List.concat [["lambda"];[(to_list_scheme (List.concat [arg1;["."];[arg2]] ))];(match body with
                                                                                                                        |Seq(lst) -> List.map to_scheme2 lst
                                                                                                                        |_ ->  [to_scheme2 body])])
  |Applic(op,lst) ->  to_list_scheme (List.concat [[to_scheme2 op];List.map to_scheme2 lst])
  |_ -> "";;


          (* and process let *)
          (*qouted to quote *)

 List.iter (fun exp -> Printf.printf "%s\n"  (to_scheme2 exp)) input;;