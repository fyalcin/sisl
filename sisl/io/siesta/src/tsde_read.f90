subroutine read_tsde_sizes(fname,nspin,no_u,nsc,nnz)

  implicit none
  
  ! Input parameters
  character(len=*), intent(in) :: fname
  integer, intent(out) :: no_u, nspin, nsc(3), nnz
  
! Define f2py intents
!f2py intent(in)  :: fname
!f2py intent(out) :: no_u, nspin, nsc, nnz

! Internal variables and arrays
  integer :: iu, ierr
  integer, allocatable :: num_col(:)

  call free_unit(iu)
  open(iu,file=trim(fname),status='old',form='unformatted')

  ! First try and see if nsc is present
  read(iu,iostat=ierr) no_u, nspin, nsc
  if ( ierr /= 0 ) then
    rewind(iu)
    read(iu) no_u, nspin
    nsc(:) = 0
  end if

  allocate(num_col(no_u))
  read(iu) num_col
  nnz = sum(num_col)
  deallocate(num_col)

  close(iu)

end subroutine read_tsde_sizes

subroutine read_tsde_dm(fname, nspin, no_u, nsc, nnz, &
     ncol,list_col,DM)

  implicit none

  ! Precision 
  integer, parameter :: sp = selected_real_kind(p=6)
  integer, parameter :: dp = selected_real_kind(p=15)

  ! Input parameters
  character(len=*), intent(in) :: fname
  integer, intent(in) :: no_u, nspin, nsc(3), nnz
  integer, intent(out) :: ncol(no_u), list_col(nnz)
  real(dp), intent(out) :: DM(nnz,nspin)
  
! Define f2py intents
!f2py intent(in)  :: fname
!f2py intent(in) :: no_u, nspin, nsc, nnz
!f2py intent(out) :: ncol, list_col
!f2py intent(out) :: DM

! Internal variables and arrays
  integer :: iu, ierr
  integer :: is, io, n

  ! Local readables
  integer :: lno_u, lnspin, lnsc(3)

  call free_unit(iu)
  open(iu,file=trim(fname),status='old',form='unformatted')

  ! First try and see if nsc is present
  read(iu,iostat=ierr) lno_u, lnspin, lnsc
  if ( ierr /= 0 ) then
    rewind(iu)
    read(iu) lno_u, lnspin
    lnsc(:) = 0
  end if
  if ( lno_u /= no_u ) stop 'Error in reading data, not allocated, no_u'
  if ( lnspin /= nspin ) stop 'Error in reading data, not allocated, nspin'
  if ( any(lnsc /= nsc) ) stop 'Error in reading data, not allocated, nsc'

  read(iu) ncol
  if ( nnz /= sum(ncol) ) stop 'Error in reading data, not allocated, nnz'

  ! Read list_col
  n = 0
  do io = 1 , no_u
     read(iu) list_col(n+1:n+ncol(io))
     n = n + ncol(io)
  end do

! Read Density matrix
  do is = 1 , nspin
     n = 0
     do io = 1 , no_u
        read(iu) DM(n+1:n+ncol(io), is)
        n = n + ncol(io)
     end do
  end do

  close(iu)

end subroutine read_tsde_dm

subroutine read_tsde_edm(fname, nspin, no_u, nsc, nnz, &
     ncol,list_col,EDM)

  implicit none

  ! Precision 
  integer, parameter :: sp = selected_real_kind(p=6)
  integer, parameter :: dp = selected_real_kind(p=15)
  real(dp), parameter :: eV = 13.60580_dp

  ! Input parameters
  character(len=*), intent(in) :: fname
  integer, intent(in) :: no_u, nspin, nsc(3), nnz
  integer, intent(out) :: ncol(no_u), list_col(nnz)
  real(dp), intent(out) :: EDM(nnz,nspin)
  
! Define f2py intents
!f2py intent(in)  :: fname
!f2py intent(in) :: no_u, nspin, nsc, nnz
!f2py intent(out) :: ncol, list_col
!f2py intent(out) :: EDM

! Internal variables and arrays
  integer :: iu, ierr
  integer :: is, io, n

  ! Local readables
  integer :: lno_u, lnspin, lnsc(3)

  call free_unit(iu)
  open(iu,file=trim(fname),status='old',form='unformatted')

  ! First try and see if nsc is present
  read(iu,iostat=ierr) lno_u, lnspin, lnsc
  if ( ierr /= 0 ) then
    rewind(iu)
    read(iu) lno_u, lnspin
    lnsc(:) = 0
  end if
  if ( lno_u /= no_u ) stop 'Error in reading data, not allocated, no_u'
  if ( lnspin /= nspin ) stop 'Error in reading data, not allocated, nspin'
  if ( any(lnsc /= nsc) ) stop 'Error in reading data, not allocated, nsc'

  read(iu) ncol
  if ( nnz /= sum(ncol) ) stop 'Error in reading data, not allocated, nnz'

  ! Read list_col
  n = 0
  do io = 1 , no_u
     read(iu) list_col(n+1:n+ncol(io))
     n = n + ncol(io)
  end do

  ! Skip density matrix
  do is = 1 , nspin
     do io = 1 , no_u
        read(iu) !
     end do
  end do

  ! Read energy density matrix
  do is = 1 , nspin
     n = 0
     do io = 1 , no_u
        read(iu) EDM(n+1:n+ncol(io), is)
        n = n + ncol(io)
     end do
     EDM(:, is) = EDM(:, is) * eV
  end do

  close(iu)

end subroutine read_tsde_edm
