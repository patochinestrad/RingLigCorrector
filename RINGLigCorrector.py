import typer
from pathlib import Path
import os
from pymol import cmd
from rich import print
from typing_extensions import Annotated
from typing import Optional

app = typer.Typer()


def format_pdb_atom_line(atom_list):
    atom_line = "{:<6s}{:>5s} {:<4s}{:>4s} {:1s}{:>4s}    {:>7s}{:>8s}{:>8s}{:>6s}{:>6s}          {:>2s}".format(
        *atom_list
    )
    return atom_line


@app.command()
def correct(
    file: Annotated[str, typer.Argument(help="Path to PDB file of the ligand")],
    compound_name: Annotated[
        str, typer.Argument(
            help="Three chracter code used to rename the ligand")
    ],
    replace_name: Annotated[
        str, typer.Argument(
            help="Name of the residue to change. Defaults to UNL")
    ] = "UNL",
    rename_chain: Annotated[
        str,
        typer.Argument(
            help="Rename the chain of the ligand or protein/ligand complex. Defaults to A"
        ),
    ] = "A",
    connections: Annotated[
        bool, typer.Option(help="Output connection scheme for use with ring")
    ] = False,
    acc_dons: Annotated[
        bool,
        typer.Option(
            help="Output hydrogen bond donor and acceptor atoms for use with ring"
        ),
    ] = False,
    outdir: Annotated[
        Optional[Path],
        typer.Option(help="Output directory. Defaults to current directory."),
    ] = os.getcwd(),
):
    """
    Rename the atoms of a small-molecule PDB file and outputs the bond order to be used with the Ring-Pymol plugin
    """
    if len(compound_name) != 3:
        print(
            """
ERROR: COMPOUND NAME NEEDS TO BE EXACTLY 3 CHARACTERS BETWEEN LETTERS AND NUMBERS!
EXITING NOW"""
        )
        return 1
    if outdir != os.getcwd():
        try:
            os.mkdir(os.path.join(os.getcwd(), outdir))
        except FileExistsError:
            print("Output directory already exists")
    with open(file, "r") as f, open(
        f"{os.path.join(outdir,compound_name)}_correct_names.pdb", "w"
    ) as fout:
        atom_dict = {}
        keep_connections = []
        atom_num = 1
        for line in f:
            if line.startswith(("ATOM", "HETATM")):
                part = line.split()
                part[-1] = "".join(x for x in part[-1] if x.isalpha())
                part[4] = rename_chain
                if part[3] != replace_name:
                    fout.write(format_pdb_atom_line(part) + "\n")
                else:
                    part[2] = part[2][0] + str(atom_num)
                    atom_num += 1
                    atom_dict[part[1]] = part[2]
                    part[3] = compound_name.upper()
                    fout.write(format_pdb_atom_line(part) + "\n")
            elif line.startswith("CONECT"):
                fout.write(line)
                parts = line.split()[1:]
                node = parts[0]
                all_connections = parts[1:]
                local_connections = list(
                    set(
                        [
                            con
                            for con in all_connections
                            if int(con) > int(node) and str(node) in atom_dict.keys()
                        ]
                    )
                )
                local_connections.insert(0, node)
                if len(local_connections) > 1:
                    keep_connections.append(local_connections)

        if connections:
            with open(
                f"{os.path.join(outdir,compound_name)}_connections_for_ring.txt", "w"
            ) as ringout:
                ringout.write(compound_name + "\n")
                for connects in keep_connections:
                    correct_naming = [atom_dict[value] for value in connects]
                    ringout.write(" ".join(correct_naming) + "\n")

    if acc_dons:
        cmd.load(f"{os.path.join(outdir,compound_name)}_correct_names.pdb")
        atoms = {"acceptors": [], "donors": []}
        cmd.select(f"(resn {compound_name} and acc.)")
        cmd.iterate("(sele)", "acceptors.append(name)", space=atoms)
        cmd.select(f"(resn {compound_name} and don.)")
        cmd.iterate("(sele)", "donors.append(name)", space=atoms)
        with open(f"{os.path.join(outdir,compound_name)}_acc_and_dons.txt", "w") as f:
            f.write(f"# {compound_name}\n")
            f.write("A:" + " ".join(atoms["acceptors"]) + "\n")
            f.write("D:" + " ".join(atoms["donors"]))


if __name__ == "__main__":
    app()
