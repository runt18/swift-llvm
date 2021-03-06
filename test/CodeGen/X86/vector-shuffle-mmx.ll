; RUN: llc < %s -mtriple=i686-darwin -mattr=+mmx,+sse2 | FileCheck --check-prefix=X32 %s
; RUN: llc < %s -mtriple=x86_64-darwin -mattr=+mmx,+sse2 | FileCheck --check-prefix=X64 %s

; If there is no explicit MMX type usage, always promote to XMM.

define void @test0(<1 x i64>* %x) {
; X32-LABEL: test0:
; X32:       ## BB#0: ## %entry
; X32-NEXT:    movl {{[0-9]+}}(%esp), %eax
; X32-NEXT:    movsd {{.*#+}} xmm0 = mem[0],zero
; X32-NEXT:    pshufd {{.*#+}} xmm0 = xmm0[1,1,2,3]
; X32-NEXT:    movq %xmm0, (%eax)
; X32-NEXT:    retl
;
; X64-LABEL: test0:
; X64:       ## BB#0: ## %entry
; X64-NEXT:    movq {{.*#+}} xmm0 = mem[0],zero
; X64-NEXT:    pshufd {{.*#+}} xmm0 = xmm0[1,1,2,3]
; X64-NEXT:    movq %xmm0, (%rdi)
; X64-NEXT:    retq
entry:
  %tmp2 = load <1 x i64>, <1 x i64>* %x
  %tmp6 = bitcast <1 x i64> %tmp2 to <2 x i32>
  %tmp9 = shufflevector <2 x i32> %tmp6, <2 x i32> undef, <2 x i32> < i32 1, i32 1 >
  %tmp10 = bitcast <2 x i32> %tmp9 to <1 x i64>
  store <1 x i64> %tmp10, <1 x i64>* %x
  ret void
}

define void @test1() {
; X32-LABEL: test1:
; X32:       ## BB#0: ## %entry
; X32-NEXT:    pushl %edi
; X32-NEXT:  Ltmp0:
; X32-NEXT:    .cfi_def_cfa_offset 8
; X32-NEXT:    subl $16, %esp
; X32-NEXT:  Ltmp1:
; X32-NEXT:    .cfi_def_cfa_offset 24
; X32-NEXT:  Ltmp2:
; X32-NEXT:    .cfi_offset %edi, -8
; X32-NEXT:    xorps %xmm0, %xmm0
; X32-NEXT:    movlps %xmm0, (%esp)
; X32-NEXT:    movq (%esp), %mm0
; X32-NEXT:    pshuflw {{.*#+}} xmm0 = mem[0,2,2,3,4,5,6,7]
; X32-NEXT:    pshufhw {{.*#+}} xmm0 = xmm0[0,1,2,3,4,6,6,7]
; X32-NEXT:    pshufd {{.*#+}} xmm0 = xmm0[0,2,2,3]
; X32-NEXT:    movq %xmm0, {{[0-9]+}}(%esp)
; X32-NEXT:    movq {{[0-9]+}}(%esp), %mm1
; X32-NEXT:    xorl %edi, %edi
; X32-NEXT:    maskmovq %mm1, %mm0
; X32-NEXT:    addl $16, %esp
; X32-NEXT:    popl %edi
; X32-NEXT:    retl
;
; X64-LABEL: test1:
; X64:       ## BB#0: ## %entry
; X64-NEXT:    xorps %xmm0, %xmm0
; X64-NEXT:    movlps %xmm0, -{{[0-9]+}}(%rsp)
; X64-NEXT:    movq -{{[0-9]+}}(%rsp), %mm0
; X64-NEXT:    pshuflw {{.*#+}} xmm0 = mem[0,2,2,3,4,5,6,7]
; X64-NEXT:    pshufhw {{.*#+}} xmm0 = xmm0[0,1,2,3,4,6,6,7]
; X64-NEXT:    pshufd {{.*#+}} xmm0 = xmm0[0,2,2,3]
; X64-NEXT:    movq %xmm0, -{{[0-9]+}}(%rsp)
; X64-NEXT:    movq -{{[0-9]+}}(%rsp), %mm1
; X64-NEXT:    xorl %edi, %edi
; X64-NEXT:    maskmovq %mm1, %mm0
; X64-NEXT:    retq
entry:
  %tmp528 = bitcast <8 x i8> zeroinitializer to <2 x i32>
  %tmp529 = and <2 x i32> %tmp528, bitcast (<4 x i16> < i16 -32640, i16 16448, i16 8224, i16 4112 > to <2 x i32>)
  %tmp542 = bitcast <2 x i32> %tmp529 to <4 x i16>
  %tmp543 = add <4 x i16> %tmp542, < i16 0, i16 16448, i16 24672, i16 28784 >
  %tmp555 = bitcast <4 x i16> %tmp543 to <8 x i8>
  %tmp556 = bitcast <8 x i8> %tmp555 to x86_mmx
  %tmp557 = bitcast <8 x i8> zeroinitializer to x86_mmx
  tail call void @llvm.x86.mmx.maskmovq( x86_mmx %tmp557, x86_mmx %tmp556, i8* null)
  ret void
}

@tmp_V2i = common global <2 x i32> zeroinitializer

define void @test2() nounwind {
; X32-LABEL: test2:
; X32:       ## BB#0: ## %entry
; X32-NEXT:    movl L_tmp_V2i$non_lazy_ptr, %eax
; X32-NEXT:    movsd {{.*#+}} xmm0 = mem[0],zero
; X32-NEXT:    unpcklps {{.*#+}} xmm0 = xmm0[0,0,1,1]
; X32-NEXT:    movlps %xmm0, (%eax)
; X32-NEXT:    retl
;
; X64-LABEL: test2:
; X64:       ## BB#0: ## %entry
; X64-NEXT:    movq _tmp_V2i@{{.*}}(%rip), %rax
; X64-NEXT:    movq {{.*#+}} xmm0 = mem[0],zero
; X64-NEXT:    pshufd {{.*#+}} xmm0 = xmm0[0,0,1,1]
; X64-NEXT:    movq %xmm0, (%rax)
; X64-NEXT:    retq
entry:
  %0 = load <2 x i32>, <2 x i32>* @tmp_V2i, align 8
  %1 = shufflevector <2 x i32> %0, <2 x i32> undef, <2 x i32> zeroinitializer
  store <2 x i32> %1, <2 x i32>* @tmp_V2i, align 8
  ret void
}

declare void @llvm.x86.mmx.maskmovq(x86_mmx, x86_mmx, i8*)
