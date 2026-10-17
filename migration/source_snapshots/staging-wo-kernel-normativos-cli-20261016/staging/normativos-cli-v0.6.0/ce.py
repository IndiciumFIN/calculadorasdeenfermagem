"""Entrada CLI única, sem alterar fingerprints das dez WOs anteriores."""
import sys


def main():
    if len(sys.argv)==1 or sys.argv[1] in ('--help','-h'):
        print('CE CLI v0.5.1 | comandos: init, run, verify, pipeline, standardize, validate-acts, normatives-universal, api-confront, supabase-confront')
        print('Uso: python ce.py <comando> --help | python ce.py supabase-confront prepare|run|verify --workspace CAMINHO')
        return
    if len(sys.argv) > 1 and sys.argv[1] == 'api-confront':
        from extensions.api_confront import main as confront_main
        sys.argv.pop(1)
        confront_main()
    elif len(sys.argv) > 1 and sys.argv[1] == 'supabase-confront':
        from extensions.supabase_confront import main as sb_main
        sys.argv.pop(1)
        sb_main()
    else:
        from ce_local.cli import main as legacy_main
        legacy_main()

if __name__ == '__main__':
    main()
