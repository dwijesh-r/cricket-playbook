#!/usr/bin/env bash
# Source this file to get agent shortcuts:
#   source ~/cricket-playbook/aliases.sh
#
# Then just type:
#   Tom Brady
#   Stephen Curry --ticket TKT-042
#   Virat Kohli
#   Kante

_cpb_chat() { cd ~/cricket-playbook && python -m scripts.claude_orchestrator.cli "$@"; }

Tom()        { if [ "$1" = "Brady" ];    then shift; _cpb_chat "Tom Brady" "$@";         else echo "Usage: Tom Brady [--ticket TKT-XXX]"; fi; }
Stephen()    { if [ "$1" = "Curry" ];    then shift; _cpb_chat "Stephen Curry" "$@";     else echo "Usage: Stephen Curry [--ticket TKT-XXX]"; fi; }
Andy()       { if [ "$1" = "Flower" ];   then shift; _cpb_chat "Andy Flower" "$@";       else echo "Usage: Andy Flower [--ticket TKT-XXX]"; fi; }
Brock()      { if [ "$1" = "Purdy" ];    then shift; _cpb_chat "Brock Purdy" "$@";       else echo "Usage: Brock Purdy [--ticket TKT-XXX]"; fi; }
Brad()       { if [ "$1" = "Stevens" ];  then shift; _cpb_chat "Brad Stevens" "$@";      else echo "Usage: Brad Stevens [--ticket TKT-XXX]"; fi; }
Florentino() { if [ "$1" = "Perez" ];    then shift; _cpb_chat "Florentino Perez" "$@";  else echo "Usage: Florentino Perez [--ticket TKT-XXX]"; fi; }
Jose()       { if [ "$1" = "Mourinho" ]; then shift; _cpb_chat "Jose Mourinho" "$@";     else echo "Usage: Jose Mourinho [--ticket TKT-XXX]"; fi; }
Ime()        { if [ "$1" = "Udoka" ];    then shift; _cpb_chat "Ime Udoka" "$@";         else echo "Usage: Ime Udoka [--ticket TKT-XXX]"; fi; }
Virat()      { if [ "$1" = "Kohli" ];    then shift; _cpb_chat "Virat Kohli" "$@";       else echo "Usage: Virat Kohli [--ticket TKT-XXX]"; fi; }
LeBron()     { if [ "$1" = "James" ];    then shift; _cpb_chat "LeBron James" "$@";      else echo "Usage: LeBron James [--ticket TKT-XXX]"; fi; }
Pep()        { if [ "$1" = "Guardiola" ];then shift; _cpb_chat "Pep Guardiola" "$@";     else echo "Usage: Pep Guardiola [--ticket TKT-XXX]"; fi; }
Jayson()     { if [ "$1" = "Tatum" ];    then shift; _cpb_chat "Jayson Tatum" "$@";      else echo "Usage: Jayson Tatum [--ticket TKT-XXX]"; fi; }
Kevin()      { if [ "$1" = "De" ] && [ "$2" = "Bruyne" ]; then shift 2; _cpb_chat "Kevin De Bruyne" "$@"; else echo "Usage: Kevin De Bruyne [--ticket TKT-XXX]"; fi; }
Kante()      { _cpb_chat "N'Golo Kante" "$@"; }
