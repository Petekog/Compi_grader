#!/bin/bash


o1=$(scheme -q < scheme_{case_num}.scm);
echo "(equal? '($o1) '({output} ))" &&\
echo "(equal? '($o1) '({output} ))" > {case_num}_test.scm  &&\
scheme -q < {case_num}_test.scm > res_{case_num}




