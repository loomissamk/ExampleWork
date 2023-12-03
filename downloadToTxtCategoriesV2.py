#loomissamk@gmail.com 

import os
import requests
from bs4 import BeautifulSoup
import re
from PyPDF2 import PdfReader
import tempfile
from multiprocessing import Process

#ensure only unique papers from subject taken.
def download_arxiv_papers(categories, master_download_path):
    os.makedirs(master_download_path, exist_ok=True)

    for category in categories:
        category_download_path = os.path.join(master_download_path, category)
        print(f"Creating directory: {category_download_path}")
        os.makedirs(category_download_path, exist_ok=True)

        temp_download_dir = tempfile.mkdtemp()
        checkpoint_file = os.path.join(category_download_path, f"{category}_checkpoint.txt")

        last_paper = get_last_paper_checkpoint(checkpoint_file)

        if last_paper:
            print(f"Resuming from paper {last_paper}")
        else:
            last_paper = 0

        page = last_paper // 2000
        paper_counter = last_paper

        while True:
            url = f"https://arxiv.org/list/{category}/new?skip={page * 2000}&show=2000"
            response = requests.get(url)

            if response.status_code != 200:
                break

            soup = BeautifulSoup(response.content, "html.parser")
            pdf_links = soup.find_all(href=re.compile(r'^/pdf/'))

            if not pdf_links:
                break

            for link in pdf_links:
                paper_counter += 1
                if paper_counter <= last_paper:
                    continue

                pdf_url = f"https://arxiv.org{link['href']}"
                title = link.text.strip()
                filename = f"{title}.pdf"
                file_path = os.path.join(temp_download_dir, filename)

                # Existing file check
                if os.path.exists(os.path.join(category_download_path, filename)):
                    print(f"Skipping '{title}' - already downloaded.")
                    continue

                try:
                    print(f"Downloading '{title}'...")
                    with open(file_path, "wb") as pdf_file:
                        pdf_response = requests.get(pdf_url)
                        pdf_file.write(pdf_response.content)
                    print(f"'{title}' downloaded successfully.")

                    # Extract text from downloaded paper and append it to the category folder's .txt file
                    pdf_text = extract_text_from_pdf(file_path)
                    if pdf_text:
                        output_txt_file = os.path.join(category_download_path, f"{category}_output.txt")
                        print(f"Writing to file: {output_txt_file}")
                        with open(output_txt_file, 'a', encoding='utf-8') as txt_file:
                            txt_file.write(f"Paper {paper_counter} - {title}\n")
                            txt_file.write(pdf_text)
                            txt_file.write("\n")
                    
                    # Update checkpoint
                    update_checkpoint(checkpoint_file, paper_counter)

                except Exception as e:
                    print(f"Failed to download '{title}': {str(e)}")

                # Remove the downloaded paper to save space
                os.remove(file_path)

            page += 1

#extract into one subject.txt file per subject.
def extract_text_from_pdf(pdf_file_path):
    try:
        with open(pdf_file_path, 'rb') as pdf_file:
            pdf_reader = PdfReader(pdf_file)
            if len(pdf_reader.pages) > 0:
                pdf_text = ""
                for page in pdf_reader.pages:
                    pdf_text += page.extract_text()
                return pdf_text
    except Exception as e:
        print(f"Error extracting text from {pdf_file_path}: {str(e)}")
    return None

#reload works.
def get_last_paper_checkpoint(checkpoint_file):
    try:
        if os.path.exists(checkpoint_file):
            with open(checkpoint_file, 'r') as file:
                last_paper = int(file.read().strip())
                return last_paper
    except Exception as e:
        print(f"Error reading checkpoint file: {str(e)}")
    return None

def update_checkpoint(checkpoint_file, last_paper):
    try:
        with open(checkpoint_file, 'w') as file:
            file.write(str(last_paper))
    except Exception as e:
        print(f"Error updating checkpoint file: {str(e)}")

#subject in subjects as it were
def download_subject_papers(subject, master_download_path):
    download_arxiv_papers({subject: arxiv_category[subject]}, master_download_path)


if __name__ == "__main__":
    master_download_path = "/home/user/Desktop/Arxiv_Papers"  # Change to your preferred master download directory, I used Ubuntu.

    #this works better when its here and not a seperate import arxiv_category.py, less errors.
    arxiv_category = {
        'CS.AI': 'Artificial Intelligence',
        'CS.AR': 'Hardware Architecture',
        'CS.CC': 'Computational Complexity',
        'CS.CE': 'Computational Engineering, Finance, and Science',
        'CS.CG': 'Computational Geometry',
        'CS.CL': 'Computation and Language',
        'CS.CR': 'Cryptography and Security',
        'CS.CV': 'Computer Vision and Pattern Recognition',
        'CS.CY': 'Computers and Society',
        'CS.DB': 'Databases',
        'CS.DC': 'Distributed, Parallel, and Cluster Computing',
        'CS.DL': 'Digital Libraries',
        'CS.DM': 'Discrete Mathematics',
        'CS.DS': 'Data Structures and Algorithms',
        'CS.ET': 'Emerging Technologies',
        'CS.FL': 'Formal Languages and Automata Theory',
        'CS.GL': 'General Literature',
        'CS.GR': 'Graphics',
        'CS.GT': 'Computer Science and Game Theory',
        'CS.HC': 'Human-Computer Interaction',
        'CS.IR': 'Information Retrieval',
        'CS.IT': 'Information Theory',
        'CS.LG': 'Machine Learning',
        'CS.LO': 'Logic in Computer Science',
        'CS.MA': 'Multiagent Systems',
        'CS.MM': 'Multimedia',
        'CS.MS': 'Mathematical Software',
        'CS.NA': 'Numerical Analysis',
        'CS.NE': 'Neural and Evolutionary Computing',
        'CS.NI': 'Networking and Internet Architecture',
        'CS.OH': 'Other Computer Science',
        'CS.OS': 'Operating Systems',
        'CS.PF': 'Performance',
        'CS.PL': 'Programming Languages',
        'CS.RO': 'Robotics',
        'CS.SC': 'Symbolic Computation',
        'CS.SD': 'Sound',
        'CS.SE': 'Software Engineering',
        'CS.SI': 'Social and Information Networks',
        'CS.SY': 'Systems and Control',
        'Econ.EM': 'Econometrics',
        'Econ.GN': 'General Economics',
        'Econ.TH': 'Theoretical Economics',
        'EESS.AS': 'Audio and Speech Processing',
        'EESS.IV': 'Image and Video Processing',
        'EESS.SP': 'Signal Processing',
        'EESS.SY': 'Systems and Control',
        'General Relativity and Quantum Cosmology': 'Gravitational physics, cosmology, and quantum gravity',
        'High Energy Physics': 'Particle physics and its associated branches',
        'Mathematical Physics': 'Intersection of mathematics and physics',
        'Nonlinear Sciences': 'Study of nonlinear phenomena',
        'Nuclear Experiment': 'Experimental nuclear physics',
        'Nuclear Theory': 'Theory of nuclear structure and reactions',
        'Physics': 'General Physics - Encompassing various fields within physics',
        'Quantitative Biology': 'Study of biological systems using quantitative techniques',
        'Quantitative Finance': 'Quantitative methods applied to finance',
        'Statistics': 'Study of data collection, analysis, interpretation, and presentation',
        'astro-ph.CO': 'Cosmology and Nongalactic Astrophysics',
        'astro-ph.EP': 'Earth and Planetary Astrophysics',
        'astro-ph.GA': 'Astrophysics of Galaxies',
        'astro-ph.HE': 'High Energy Astrophysical Phenomena',
        'astro-ph.IM': 'Instrumentation and Methods for Astrophysics',
        'astro-ph.SR': 'Solar and Stellar Astrophysics',
        'condensed_matter': 'Condensed Matter Physics - Properties of condensed matter, including solids and liquids',
        'math.AC': 'Commutative Algebra',
        'math.AG': 'Algebraic Geometry',
        'math.AP': 'Analysis of PDEs',
        'math.AT': 'Algebraic Topology',
        'math.CA': 'Classical Analysis and ODEs',
        'math.CO': 'Combinatorics',
        'math.CT': 'Category Theory',
        'math.CV': 'Complex Variables',
        'math.DG': 'Differential Geometry',
        'math.DS': 'Dynamical Systems',
        'math.FA': 'Functional Analysis',
        'math.GM': 'General Mathematics',
        'math.GN': 'General Topology',
        'math.GR': 'Group Theory',
        'math.GT': 'Geometric Topology',
        'math.HO': 'History and Overview',
        'math.IT': 'Information Theory',
        'math.KT': 'K-Theory and Homology - Algebraic and topological K-theory, relations with topology, commutative algebra, and operator algebras',
        'math.LO': 'Logic - Logic, set theory, point-set topology, formal mathematics',
        'math.MG': 'Metric Geometry - Euclidean, hyperbolic, discrete, convex, coarse geometry, comparisons in Riemannian geometry, symmetric spaces',
        'math.MP': 'Mathematical Physics - Application of mathematics to problems in physics, mathematical methods for applications, mathematically rigorous formulations of existing physical theories',
        'math.NA': 'Numerical Analysis - Numerical algorithms for problems in analysis and algebra, scientific computation',
        'math.NT': 'Number Theory - Prime numbers, diophantine equations, analytic number theory, algebraic number theory, arithmetic geometry, Galois theory',
        'math.OA': 'Operator Algebras - Algebras of operators on Hilbert space, C^*-algebras, von Neumann algebras, non-commutative geometry',
        'math.OC': 'Optimization and Control - Operations research, linear programming, control theory, systems theory, optimal control, game theory',
        'math.PR': 'Probability - Theory and applications of probability and stochastic processes',
        'math.QA': 'Quantum Algebra - Quantum groups, skein theories, operadic and diagrammatic algebra, quantum field theory',
        'math.RA': 'Rings and Algebras - Non-commutative rings and algebras, non-associative algebras, universal algebra and lattice theory, linear algebra, semigroups',
        'math.RT': 'Representation Theory - Linear representations of algebras and groups, Lie theory, associative algebras, multilinear algebra',
        'math.SG': 'Symplectic Geometry - Hamiltonian systems, symplectic flows, classical integrable systems',
        'math.SP': 'Spectral Theory - Schrodinger operators, operators on manifolds, general differential operators, numerical studies, integral operators, discrete models, resonances',
        'math.ST': 'Statistics Theory - Applied, computational and theoretical statistics',
        'nlin.AO': 'Adaptation and Self-Organizing Systems',
        'nlin.CG': 'Cellular Automata and Lattice Gases',
        'nlin.CD': 'Chaotic Dynamics',
        'nlin.SI': 'Exactly Solvable and Integrable Systems',
        'nlin.PS': 'Pattern Formation and Solitons',
        'nucl-ex': 'Nuclear Experiment',
        'nucl-th': 'Nuclear Theory',
        'physics.acc-ph': 'Accelerator Physics',
        'physics.app-ph': 'Applied Physics',
        'physics.ao-ph': 'Atmospheric and Oceanic Physics',
        'physics.atom-ph': 'Atomic Physics',
        'physics.atm-clus': 'Atomic and Molecular Clusters',
        'physics.bio-ph': 'Biological Physics',
        'physics.chem-ph': 'Chemical Physics',
        'physics.class-ph': 'Classical Physics',
        'physics.comp-ph': 'Computational Physics',
        'physics.data-an': 'Data Analysis, Statistics and Probability',
        'physics.flu-dyn': 'Fluid Dynamics',
        'physics.gen-ph': 'General Physics',
        'physics.geo-ph': 'Geophysics',
        'physics.hist-ph': 'History and Philosophy of Physics',
        'physics.ins-det': 'Instrumentation and Detectors',
        'physics.med-ph': 'Medical Physics',
        'physics.optics': 'Optics',
        'physics.ed-ph': 'Physics Education',
        'physics.soc-ph': 'Physics and Society',
        'physics.plasm-ph': 'Plasma Physics',
        'physics.pop-ph': 'Popular Physics',
        'physics.space-ph': 'Space Physics',
        'q-bio.BM': 'Biomolecules',
        'q-bio.CB': 'Cell Behavior',
        'q-bio.GN': 'Genomics',
        'q-bio.MN': 'Molecular Networks',
        'q-bio.NC': 'Neurons and Cognition',
        'q-bio.OT': 'Other Quantitative Biology',
        'q-bio.PE': 'Populations and Evolution',
        'q-bio.QM': 'Quantitative Methods',
        'q-bio.SC': 'Subcellular Processes',
        'q-bio.TO': 'Tissues and Organs',
        'q-fin.CP': 'Computational Finance',
        'q-fin.EC': 'Economics',
        'q-fin.GN': 'General Finance',
        'q-fin.MF': 'Mathematical Finance',
        'q-fin.PM': 'Portfolio Management',
        'q-fin.PR': 'Pricing of Securities',
        'q-fin.RM': 'Risk Management',
        'q-fin.ST': 'Statistical Finance',
        'q-fin.TR': 'Trading and Market Microstructure',
        'stat.AP': 'Applications',
        'stat.CO': 'Computation',
        'stat.ML': 'Machine Learning',
        'stat.ME': 'Methodology',
        'stat.OT': 'Other Statistics',
        'stat.TH': 'Statistics Theory',
    }

    # Run downloads concurrently for each subject
    processes = []
    for subject in arxiv_category:
        process = Process(target=download_subject_papers, args=(subject, master_download_path))
        processes.append(process)
        process.start()

    # Wait for all processes to complete
    for process in processes:
        process.join()
        
    #hope you got a server it's a lot of processes! 
    download_arxiv_papers(arxiv_category, master_download_path)
